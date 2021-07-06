using RCDSystem.Class.PLC;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Threading;

namespace ConsoleApp3
{
    class DataManager
    {
        Dictionary<string, PLC_MineStorage> Dic = new Dictionary<string, PLC_MineStorage>();
        PLCManager PLCManager;
        MineManager MineManager;

        public DataManager()
        {
            Init_MineStorage();
            PLCManager = new PLCManager();
            PLCManager.Request_Recive += ReciveData;
            MineManager = new MineManager();
            MineManager.Event_StorageComp += Event_Storage;
            MineManager.Event_MoveComp += Event_Move;
            MineManager.Event_UnloadComp += Event_Unload;
        }

        public void Update()
        {
            MineManager.Update();

            foreach (var item in Dic)
            {
                string key = item.Key;

                if (MineManager.MineCountDic.ContainsKey(key))
                {
                    int count = MineManager.MineCountDic[key];
                    Dic[key].SetCurrent(count);
                }
            }

            PLC_SendMessage message_MineState = CreateMessage(PLC_MessageType.LoadingState, Dic);
            PLCManager.SendData(message_MineState);
        }
        private void ReciveData(object obj)
        {
            if (obj is PLC_Receive_DropMine Dropmine)
            {
                Receive_DropMine(Dropmine);
            }
            if (obj is PLC_Receive_StorageMine Storagemine)
            {
                Receive_StorageMine(Storagemine);
            }
            if (obj is PLC_Receive_MoveMine Movemine)
            {
                Receive_MoveMine(Movemine);
            }
            if (obj is PLC_Receive_UnloadMine Unloadmine)
            {
                Receive_UnloadMine(Unloadmine);
            }
        }

        private PLC_SendMessage CreateMessage(PLC_MessageType type, object data)
        {
            PLC_SendMessage message = new PLC_SendMessage()
            {
                Type = type,
                Data = data
            };
            return message;
        }

        private void Init_MineStorage()
        {
            for (int i = 0; i < 2; i++)
            {
                string key = i == 0 ? "L_" : "R_";

                for (int j = 1; j < 5; j++)
                {
                    string Rowkey = key + j + "_";

                    for (int x = 1; x < 6; x++)
                    {
                        string Colkey = Rowkey + x;

                        PLC_MineStorage mine = new PLC_MineStorage(Colkey, "mine");

                        Dic.Add(Colkey, mine);
                    }
                }
            }
        }

        //Drop
        private void Receive_DropMine(PLC_Receive_DropMine data)
        {
            Event_Drop(data.Pos, data.MineName);
        }

        private void Event_Drop(string pos, string mineName)
        {
            bool IsSuccess  = MineManager.Event_Drop(pos, mineName);

            PLC_Send_DropMine drop = new PLC_Send_DropMine
            {
                Pos = pos,
                MineName = mineName,
                Result = IsSuccess,
                CurrentTime = DateTime.Now.ToString("s")
            };
            PLC_SendMessage message = CreateMessage(PLC_MessageType.Drop, drop);
            PLCManager.SendData(message);
        }

        //적재
        private void Receive_StorageMine(PLC_Receive_StorageMine data)
        {
            MineManager.AddLoading(data);
        }

        private void Event_Storage(string pos, string mineName, int num, bool result)
        {
            PLC_Send_StorageMine storage = new PLC_Send_StorageMine
            {
                Pos = pos,
                MineName = mineName,
                Result = result,
                StorageNum = num,
                CurrentNum = MineManager.Get_CurrentCount(pos),
                CurrentTime = DateTime.Now.ToString("s")
            };
            PLC_SendMessage message = CreateMessage(PLC_MessageType.Storage, storage);
            PLCManager.SendData(message);

        }

        //이동 
        public void Receive_MoveMine(PLC_Receive_MoveMine data)
        {
            MineManager.AddLoading(data);
        }

        private void Event_Move(string sendPos, string receivePos, string mineName, int sendCount, int receiveCount, bool result, int moveNum = 1)
        {
            PLC_Send_MoveMine move = new PLC_Send_MoveMine
            {
                SendPos = sendPos,
                RecivePos = receivePos,
                Result = result,
                MoveNum = moveNum,
                MineName = mineName,
                SendMineCurCount = sendCount,
                ReceiveMineCurCount = receiveCount,
                CurrentTime = DateTime.Now.ToString("s")
            };
            PLC_SendMessage message = CreateMessage(PLC_MessageType.Move, move);
            PLCManager.SendData(message);
        
        }

        //하역 
        public void Receive_UnloadMine(PLC_Receive_UnloadMine data)
        {
            MineManager.AddLoading(data);
        }

        private void Event_Unload(string pos, string mineName, bool result, int unloadNum = 1)
        {
            PLC_Send_UnloadMine unload = new PLC_Send_UnloadMine
            {
                Pos = pos,
                MineName = mineName,
                Result = result,
                UnloadNum = unloadNum,
                RemainNum = MineManager.Get_CurrentCount(pos),
                CurrentTime = DateTime.Now.ToString("s")
            };
            PLC_SendMessage message = CreateMessage(PLC_MessageType.Unload, unload);
            PLCManager.SendData(message);
        }
        
    }
}
