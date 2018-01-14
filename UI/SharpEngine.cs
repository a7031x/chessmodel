using csmodel;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace UI
{
    class SharpEngine
    {
        private SearchEngine _engine;
        public SharpEngine()
        {
            var folder = AppDomain.CurrentDomain.BaseDirectory;
            folder = Directory.GetParent(folder).Parent.Parent.Parent.FullName;
            folder = Path.Combine(folder, "chessmodel", "model", "1.4");
            var model = new Model(folder);
            _engine = new SearchEngine(model);
        }

        public SearchEngine.SearchItem Advice(byte[] chessBoard, bool red)
        {
            var board = Utility.TransformBoard(chessBoard, ' ');
            var results = _engine.Search(board, red, 4);
            return results[0];
        }
    }
}
