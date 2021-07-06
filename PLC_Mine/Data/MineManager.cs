using RCDSystem.Class.PLC;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Threading;
using PLC_Mine.Helper;

namespace PLC_Mine
{
    class MineManager
    {
        
        public Dictionary<string, List<Mine>> MineDic { get; private set; }
        public Dictionary<string, int> MineCountDic { get; private set; }

        TimerHelper timerHelper;

        public MineManager()
        {
            Init_MineStorage();
            timerHelper = new TimerHelper(1f);
        }

        public void Update()
        {
            foreach (var item in MineCountDic)
            {
                string key = item.Key;
                MineCountDic[key] = Get_CurrentCount(key);
            }
            Update_Loading();
        }

        public void AddLoading(object _data)
        {
            if (_data is PLC_Receive_StorageMine storage)
            {
                if(CanEvent(storage.Pos, storage.Num, true))
                {
                    for (int i = 0; i < storage.Num; i++)
                    {
                        StorageQueue.Enqueue(storage);
                    }
                }
                else
                {
                    Event_StorageComp(storage.Pos, storage.MineName, storage.Num, false);
                }
                
            }

            if (_data is PLC_Receive_MoveMine move)
            {
                if(CanEvent(move.SendPos, move.MoveNum, false) && CanEvent(move.RecivePos, move.MoveNum, true))    
                {
                    for (int i = 0; i < move.MoveNum; i++)
                    {
                        MoveQueue.Enqueue(move);
                    }
                }
                else
                {
                    Event_MoveComp(move.SendPos, move.RecivePos, move.SendMineName, Get_CurrentCount(move.SendPos), Get_CurrentCount(move.RecivePos), false, move.MoveNum);
                }
                
            }

            if (_data is PLC_Receive_UnloadMine unload)
            {
                if(CanEvent(unload.Pos, unload.UnloadNum, false))
                {
                    for (int i = 0; i < unload.UnloadNum; i++)
                    {
                        UnloadQueue.Enqueue(unload);
                    }
                }
                else
                {
                    Event_UnloadComp(unload.Pos, unload.MineName, false, unload.UnloadNum);
                }
            }
        }

        Queue<PLC_Receive_StorageMine> StorageQueue = new Queue<PLC_Receive_StorageMine>();
        Queue<PLC_Receive_MoveMine> MoveQueue = new Queue<PLC_Receive_MoveMine>();
        Queue<PLC_Receive_UnloadMine> UnloadQueue = new Queue<PLC_Receive_UnloadMine>();

        bool isStop;
        private void Update_Loading()
        {
            if (!(timerHelper != null && timerHelper.IsTimer())) return;

            if (StorageQueue.Count > 0)
            {
                if(!isStop)
                {
                    PLC_Receive_StorageMine storageMine = StorageQueue.Dequeue();
                    Event_Storage(storageMine.Pos, storageMine.MineName);
                }
                
            }

            if(MoveQueue.Count > 0)
            {
                if (!isStop)
                {
                    PLC_Receive_MoveMine moveMine = MoveQueue.Dequeue();
                    Event_Move(moveMine.SendPos, moveMine.RecivePos, moveMine.SendMineName);
                }
            }

            if(UnloadQueue.Count > 0)
            {
                if (!isStop)
                {
                    PLC_Receive_UnloadMine unloadMine = UnloadQueue.Dequeue();
                    Event_Unload(unloadMine.Pos, unloadMine.MineName);
                }
            }
        }

        public void Init_MineStorage(Dictionary<string, PLC_MineStorage> Dic)
        {
            foreach (var item in Dic)
            {
                string key = item.Key;
                PLC_MineStorage storage = item.Value;
                if (MineDic.ContainsKey(key))
                {
                    List<Mine> list = MineDic[key];

                    for (int i = 0; i < storage.CurrentCount; i++)
                    {
                        list[i].IsFull = true;
                    }
                }
            }
        }

        private void Init_MineStorage()
        {
            MineDic = new Dictionary<string, List<Mine>>();
            MineCountDic = new Dictionary<string, int>();

            for (int i = 0; i < 2; i++)
            {
                string key = i == 0 ? "L_" : "R_";

                for (int j = 1; j < 5; j++)
                {
                    string Rowkey = key + j + "_";

                    for (int k = 1; k < 6; k++)
                    {
                        List<Mine> Mine_List = new List<Mine>();
                        string Colkey = Rowkey + k;

                        for (int p = 1; p < 13; p++)
                        {
                            string mineKey = Colkey + "_" + p;
                            Mine mine = new Mine(mineKey, "mine", false);

                            Mine_List.Add(mine);
                        }

                        MineDic.Add(Colkey, Mine_List);
                        MineCountDic.Add(Colkey, 0);
                    }
                }
            }
        }

        private bool IsKey(string key)
        {
            return MineDic.ContainsKey(key);
        }

        private bool IsEqualsMineName(string key, string mineName)
        {
            if (!MineDic.ContainsKey(key)) return false;
            return Get_MineName(key).Equals(mineName);
        }

        public int Get_CurrentCount(string key)
        {
            Mine cur = GetCurrentMine(key);
            int count = cur != null ? cur.Num : 0;
            return count;
        }

        private Mine GetCurrentMine(string key)
        {
            if (!IsKey(key)) return null;
            Mine mine = null;
            List<Mine> list = MineDic[key];
            for (int i = 0; i < list.Count; i++)
            {
                if (!list[i].IsFull)
                {
                    break;
                }
                mine = list[i];
            }
            return mine;
        }

        private string Get_MineName(string key)
        {
            Mine mine = GetCurrentMine(key);
            string name = mine != null ? mine.MineName : "mine";
            return name;
        }

        private void SetMineList_MineName(string key, string mineName)
        {
            if (!IsKey(key)) return;
            List<Mine> list = MineDic[key];
            int minecount = Get_CurrentCount(key);
            if (minecount == 0)
            {
                SetMineList_MineName(list, mineName);
            }
        }

        private void SetMineList_MineName(List<Mine> list, string mineName)
        {
            for (int i = 0; i < list.Count; i++)
            {
                list[i].MineName = mineName;
            }
        }

        private void Set_MineState(List<Mine> list, int num, bool check)
        {
            if(check)
            {
                list[num].IsFull = true;
            }
            else
            {
                list[num-1].IsFull = false;
            }
        }

        private void Set_MineState(string key, string mineName, int num, bool check)
        {
            if (IsEqualsMineName(key, mineName))
            {
                Set_MineState(MineDic[key], num, check);
            }
        }

        private bool CanEvent(string key, int moveNum, bool check)
        {
            if (!IsKey(key)) return false;

            if (check) return Get_CurrentCount(key) + moveNum < MineDic[key].Count;

            return Get_CurrentCount(key) - moveNum > 0;
        }

        //드랍
        public bool Event_Drop(string key, string mineName)
        {
            if (!IsKey(key)) return false;

            Mine mine = GetCurrentMine(key);
            if (mine == null) return false;
            if (!mine.MineName.Equals(mineName)) return false;

            mine.IsFull = false;
            return true;
        }

        public Action<string, string, int, bool> Event_StorageComp = new Action<string, string, int, bool>(delegate { });
        //적재
        public void Event_Storage(string key, string mineName)
        {
            if (!IsKey(key))
            {
                Event_StorageComp(key, mineName, 1, false);

                return ;
            }

            SetMineList_MineName(key, mineName);

            if (!IsEqualsMineName(key,mineName)) 
            {
                Event_StorageComp(key, mineName, 1, false);

                return; 
            }

            int minecount = Get_CurrentCount(key);

            Set_MineState(key, mineName, minecount, true);
            Event_StorageComp(key, mineName, 1, true);

        }

        public Action<string, string, string, int, int, bool, int> Event_MoveComp = new Action<string, string, string, int, int, bool, int>(delegate { });
        //이동
        public void Event_Move(string sendKey, string receiveKey, string sendmineName)
        {
            if (!IsKey(sendKey) && !IsKey(receiveKey))
            {
                Event_MoveComp(sendKey, receiveKey, sendmineName, Get_CurrentCount(sendKey), Get_CurrentCount(receiveKey), false, 1);
                return;
            }
            
            SetMineList_MineName(receiveKey, sendmineName);

            if (!IsEqualsMineName(sendKey, Get_MineName(receiveKey)))
            {
                Event_MoveComp(sendKey, receiveKey, sendmineName, Get_CurrentCount(sendKey), Get_CurrentCount(receiveKey), false, 1);

                return;
            }

            int send_Currentcount = Get_CurrentCount(sendKey);
            int receieve_Currentcount = Get_CurrentCount(receiveKey);

            Set_MineState(sendKey, sendmineName, send_Currentcount, false);
            Set_MineState(receiveKey, sendmineName, receieve_Currentcount, true);

            Event_MoveComp(sendKey, receiveKey, sendmineName, Get_CurrentCount(sendKey), Get_CurrentCount(receiveKey), true, 1);

        }

        public Action<string, string, bool, int> Event_UnloadComp = new Action<string, string, bool, int>(delegate { });
        //하역
        public void Event_Unload(string key, string mineName)
        {
            if (!IsKey(key))
            {
                Event_UnloadComp(key, mineName, false, 1);
                return;
            }

            if (!IsEqualsMineName(key, mineName))
            {
                Event_UnloadComp(key, mineName, false, 1);
                return;
            }
         
            int current_Count = Get_CurrentCount(key);

            Set_MineState(key, mineName, current_Count, false);
            Event_UnloadComp(key, mineName, true, 1);
        }
    }
}
