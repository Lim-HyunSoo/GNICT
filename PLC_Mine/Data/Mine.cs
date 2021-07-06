using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ConsoleApp3
{
    [Serializable]
    class Mine
    {
        public string Pos { get; set; }
        public string MineName { get; set; }
        public bool Direction { get; set; } // L 이 true 
        public int Row { get; set; }
        public int Col { get; set; }
        public int Num { get; set; }
        public bool IsFull { get; set; }
      
        public Mine(string key, string mineName = "", bool isFull = false)
        {
            SetPosition(key);
            MineName = mineName;
            IsFull = isFull;
        }

        public Mine(string pos, string mineName, bool direction, int row, int col, int num, bool isFull)
        {
            Pos = pos;
            MineName = mineName;
            Direction = direction;
            Row = row;
            Col = col;
            Num = num;
            IsFull = isFull;
        }

        public string GetDirection_String()
        {
            return Direction ? "L" : "R";
        }

        public string CreatePos()
        {
            return GetDirection_String() + "_" + Col + "_" + Row + "_" + Num;
        }

        public void SetPosition(string pos)
        {
            try
            {
                string[] split = Pos.Split('_');
                Direction = split[0].Trim().Equals("L");
                Col = int.Parse(split[1]);
                Row = int.Parse(split[2]);
                Num = int.Parse(split[3]);
            }
            catch { }
        }
    }
}
