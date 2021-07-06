using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.NetworkInformation;
using System.Runtime.Serialization.Formatters.Binary;
using System.Text;
using System.Threading.Tasks;

namespace MCnCSystem.Class.Helper
{
    public static class Helper
    {
        public static string GetMacAddress()
        {
            return NetworkInterface.GetAllNetworkInterfaces()[0].GetPhysicalAddress().ToString();
        }
    }

    public static class StringHelper
    {
        public static string SubString(string text, string start, string end, out string NextText)
        {
            NextText = "";
            try
            {
                int startPos = text.IndexOf(start);
                int Start = startPos + start.Length;
                int End = text.IndexOf(end);
                if(End != -1)
                {
                    int next = End + end.Length;
                    if(Start<End)
                    {
                        string result = text.Substring(Start, End - Start).Trim();
                        if (text.Length > next)
                        {
                            NextText = text.Substring(next).Trim();
                        }
                       
                        return result;
                    }
                    else
                    {
                        string error = text.Substring(startPos).Trim();

                        return SubString(error, start, end, out NextText);
                    }
                }
            }
            catch
            {
                return "";
            }
            return "";
        }
    }

    static class ConvertHelper
    {

        public static byte[] StringToBytes(string str)
        {
            return Encoding.UTF8.GetBytes(str);
        }

        public static string BytesToString(byte[] bytes)
        {
            return Encoding.Default.GetString(bytes).Trim('\0');
        }

        public static string BytesToString_UTF8(byte[] bytes)
        {
            return Encoding.UTF8.GetString(bytes).Trim('\0');
        }

        public static string GetJsonType(string json)
        {
            string[] split = json.Split('{');
            if (!(split.Length > 0)) return "";
            return split[0].Replace("{", "").Trim();
        }

        public static byte[] ObjectToByteArray(object obj)
        {
            if (obj == null)
                return null;
            BinaryFormatter bf = new BinaryFormatter();
            using (MemoryStream ms = new MemoryStream())
            {
                bf.Serialize(ms, obj);
                return ms.ToArray();
            }
        }
    }
}
