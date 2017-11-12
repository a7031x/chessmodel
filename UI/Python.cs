using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace UI
{
    class Python
    {
        private StreamReader _reader;
        private StreamWriter _writer;
        public static Python Instance = new Python();
        static Python()
        {
            Instance.Start();
        }

        public void Start()
        {
            string python = "python.exe";
            string folder = AppDomain.CurrentDomain.BaseDirectory;
            folder = Directory.GetParent(python).Parent.Parent.Parent.FullName;
            folder = Path.Combine(folder, "chessmodel");
            var chessmodel = Path.Combine(folder, $"main.py --output_dir {Path.Combine(folder, "output")}");

            var info = new ProcessStartInfo(python)
            {
                UseShellExecute = false,
                WindowStyle = ProcessWindowStyle.Hidden,
                RedirectStandardInput = true,
                RedirectStandardOutput = true,
                Arguments = chessmodel
            };
            var process = new Process
            {
                StartInfo = info
            };
            process.Start();
            _writer = process.StandardInput;
            _reader = process.StandardOutput;
            while (_reader.ReadLine() != "ready") ;
        }

        public string Call(string command)
        {
            _writer.WriteLine(command);
            return _reader.ReadLine();
        }

        public String TransformBoard(byte[] board)
        {
            var r = string.Empty;
            foreach (var c in board)
                r += TransformChess(c);
            return r;
        }

        public char TransformChess(byte chess)
        {
            switch (chess)
            {
                case 256 - 6: return 'r';
                case 256 - 2: return 'h';
                case 256 - 5: return 'e';
                case 256 - 4: return 'b';
                case 256 - 3: return 'k';
                case 256 - 7: return 'c';
                case 256 - 1: return 'p';
                case 6: return 'R';
                case 2: return 'H';
                case 5: return 'E';
                case 4: return 'B';
                case 3: return 'K';
                case 7: return 'C';
                case 1: return 'P';
                default: return '#';
            }
        }

        public IEnumerable<Tuple<int, int>> GetMoves(byte[] chessBoard, bool red)
        {
            var board = TransformBoard(chessBoard);
            var command = $"get_moves {(red ? 1 : 0)} {board}";
            var response = Call(command);
            var tokens = response
                .Split(new[] { '[', ']', '(', ')', ',', ' ' }, StringSplitOptions.RemoveEmptyEntries)
                .Select(int.Parse)
                .ToArray();
            var r = new List<Tuple<int, int>>();
            for(int k = 0; k < tokens.Length / 2; ++k)
            {
                var t = Tuple.Create(tokens[k * 2], tokens[k * 2 + 1]);
                r.Add(t);
            }
            return r;
        }

        public double GetScore(byte[] chessBoard, bool red)
        {
            var board = TransformBoard(chessBoard);
            var command = $"evaluate {(red ? 1 : 0)} {board}";
            var response = Call(command);
            return double.Parse(response);
        }
    }
}
