using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace ConsoleApp3
{
    [Serializable]
    public class PLC_MineStorage
    {
        public string Pos { get; set; }
        public string MineName { get; set; }
        public int CurrentCount { get; set; }
        public int MaxCount { get; set; }
        public PLC_MineStorage(string pos, string mineName, int currentCount = 0, int maxCount = 12)
        {
            Pos = pos;
            MineName = mineName;
            CurrentCount = currentCount;
            MaxCount = maxCount;
        }
        public void SetCurrent(int current)
        {
            CurrentCount = current;
        }
        public void SetMax(int max)
        {
            MaxCount = max;
        }
    }

    [Serializable]
    public struct PLC_Receive_DropMine
    {
        public string Pos { get; set; }
        public string MineName { get; set; }
    }

    [Serializable]
    public struct PLC_Send_DropMine
    {
        public bool Result { get; set; }
        public string Pos { get; set; }
        public string MineName { get; set; }
        public string CurrentTime { get; set; }
    }

    [Serializable]
    public struct PLC_Receive_StorageMine
    {
        public string Pos { get; set; }
        public string MineName { get; set; }
        public int Num { get; set; }
    }

    [Serializable]
    public struct PLC_Send_StorageMine
    {
        public bool Result { get; set; }
        public string Pos { get; set; }
        public string MineName { get; set; }
        public int StorageNum { get; set; }
        public int CurrentNum { get; set; }
        public string CurrentTime { get; set; }
    }

    [Serializable]
    public struct PLC_Receive_MoveMine
    {
        public string SendPos { get; set; }
        public string RecivePos { get; set; }
        public string SendMineName { get; set; }
        public int MoveNum { get; set; }
    }

    [Serializable]
    public struct PLC_Send_MoveMine
    {
        public bool Result { get; set; }
        public string SendPos { get; set; }
        public string RecivePos { get; set; }
        public string MineName { get; set; }
        public int SendMineCurCount { get; set; }
        public int ReceiveMineCurCount { get; set; }
        public int MoveNum { get; set; }
        public string CurrentTime { get; set; }
    }

    [Serializable]
    public struct PLC_Receive_UnloadMine
    {
        public string Pos { get; set; }
        public string MineName { get; set; }
        public int UnloadNum { get; set; }
    }

    [Serializable]
    public struct PLC_Send_UnloadMine
    {
        public string Pos { get; set; }
        public string MineName { get; set; }
        public bool Result { get; set; }
        public int UnloadNum { get; set; }
        public int RemainNum { get; set; }
        public string CurrentTime { get; set; }
    }

}