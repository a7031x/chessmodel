﻿using System;
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
            string python = "\"C:\\Program Files (x86)\\Microsoft Visual Studio\\Shared\\Python36_64\\python.exe\"";
            string folder = AppDomain.CurrentDomain.BaseDirectory;
            folder = Directory.GetParent(folder).Parent.Parent.Parent.FullName;
            folder = Path.Combine(folder, "chessmodel");
            var chessmodel = Path.Combine(folder, $"main.py --output_dir {Path.Combine(folder, "output")}");

            var info = new ProcessStartInfo(python)
            {
                UseShellExecute = false,
                WindowStyle = ProcessWindowStyle.Hidden,
                RedirectStandardInput = true,
                RedirectStandardOutput = true,
                WorkingDirectory = folder,
                Arguments = chessmodel
            };
            var process = new Process
            {
                StartInfo = info
            };
            process.Start();
            _writer = process.StandardInput;
            _reader = process.StandardOutput;
            while (true)
            {
                var line = _reader.ReadLine();
                if (null == line)
                    continue;
                if (line == "ready")
                    break;
                Debug.WriteLine(line);
            }
        }

        public string Call(string command)
        {
            _writer.WriteLine(command);
            var r = _reader.ReadLine();
            Debug.WriteLine(r);
            return r;
        }

        public IEnumerable<Tuple<int, int>> GetMoves(byte[] chessBoard, bool red)
        {
            var board = Utility.TransformBoard(chessBoard);
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

        public Tuple<double, double> GetScore(byte[] chessBoard, bool red)
        {
            var board = Utility.TransformBoard(chessBoard);
            var command = $"evaluate {(red ? 1 : 0)} {board}";
            var response = Call(command);
            var scores = response.Split(' ');
            return Tuple.Create(double.Parse(scores[0]), double.Parse(scores[1]));
        }

        public int[] Advice(byte[] chessBoard, bool red)
        {
            var board = Utility.TransformBoard(chessBoard);
            var command = $"advice {(red ? 1 : 0)} {board}";
            var response = Call(command);
            var numbers = response.Split(new[] { '(', ')', ',', ' ' }, StringSplitOptions.RemoveEmptyEntries).ToArray();
            var move = numbers.Select(float.Parse).Select(x => (int)x).ToArray();
            return move;
        }

        internal Tuple<int, int> Evaluate(byte[] chessBoard, bool red)
        {
            var board = Utility.TransformBoard(chessBoard);
            var command = $"evaluate {(red ? 1 : 0)} {board}";
            var response = Call(command);
            var move = response.Split(new[] { '(', ')', ',', ' ' }, StringSplitOptions.RemoveEmptyEntries).Select(int.Parse);
            return Tuple.Create(move.First(), move.Last());
        }
    }
}
