using MCnCSystem.Class.Helper;
using System;
using System.Collections.Generic;
using System.Text;

namespace ConsoleApp7.PLC
{
    class BufferHelper
    {
        private List<byte> buffer = new List<byte>();
        private List<byte[]> ReciveDatas = new List<byte[]>();
        static string StartMessage = "<Start>";
        static string EndMessage = "<End>";

        public List<byte[]> GetDatas()
        {
            List<byte[]> rs = ReciveDatas;
            ReciveDatas = new List<byte[]>();
            return rs;
        }

        public static byte[] CreateData(byte[] Data)
        {
            string str = ConvertHelper.BytesToString_UTF8(Data);
            string sData = StartMessage + str + EndMessage;
            return ConvertHelper.StringToBytes(sData);
        }

        public bool AddBuffer(byte[] Data)
        {
            buffer.AddRange(Data);
            string str = ConvertHelper.BytesToString_UTF8(buffer.ToArray());

            bool isStart = str.Contains(StartMessage);
            bool isEnd = str.Contains(EndMessage);
            bool isSuccess = false;

            if (isStart && isEnd)
            {
                while (true)
                {
                    string result = StringHelper.SubString(str, StartMessage, EndMessage, out string next);
                    if (!string.IsNullOrEmpty(result))
                    {
                        byte[] resultData = ConvertHelper.StringToBytes(result);
                        ReciveDatas.Add(resultData);
                        str = next;
                        isSuccess = true;
                    }
                    else
                    {
                        buffer = new List<byte>();
                        if (!string.IsNullOrEmpty(str))
                        {
                            byte[] nextData = ConvertHelper.StringToBytes(str);
                            buffer.AddRange(nextData);
                        }
                        break;
                    }
                }
            }

            return isSuccess;
        }
    }
}
