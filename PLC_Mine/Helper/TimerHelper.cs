using System;
using System.Collections.Generic;
using System.Text;

namespace ConsoleApp3.Helper
{
    class TimerHelper
    {
        float delay;
        DateTime current;
        public TimerHelper(float _delay)
        {
            delay = _delay;
            current = DateTime.Now;
        }

        public bool IsTimer()
        {
            TimeSpan timeSpan = DateTime.Now - current;
            if (timeSpan.TotalSeconds > delay)
            {
                current = DateTime.Now;
                return true;
            }
            return false;
        }
    }
}
