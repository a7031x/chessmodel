using csmodel;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace test
{
    class Program
    {
        static void Main(string[] args)
        {
            var model = new Model(@"E:\projects\github\chessmodel\chessmodel\model\1.4");
            var board = "rnbakabnr##########c#####c#p#p#p#p#p##################P#P#P#P#P#C#####C##########RNBAKABNR".Replace('#', ' ');
            var scores = model.Predict(new[] { board }, true);
            Console.WriteLine(scores);
        }
    }
}
