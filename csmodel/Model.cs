using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using TensorFlow;

namespace csmodel
{
    public class Model
    {
        private TFSession session;
        public Model(string path)
        {
            var graph = new TFGraph();
            var metaGraph = new TFBuffer();
            session = new TFSession();
            var sess = session.FromSavedModel(new TFSessionOptions(), null, path, new[] { "serve" }, graph, metaGraph);
            session = sess;
        }

        public float[] Predict(string[] boards, bool red)
        {
            var mlen = 1;
            var squareBuffer = new int[boards.Length * 90 * mlen * 2];
            var lengthBuffer = new int[boards.Length * 90];
            for(var k = 0; k < 90; ++k)
            {
                squareBuffer[k * 2] = 14;
                squareBuffer[k * 2 + 1] = 0;
                lengthBuffer[k] = 1;
            }
            var inputSquare = TFTensor.FromBuffer(new TFShape(boards.Length, 90, mlen, 2), squareBuffer, 0, squareBuffer.Length);
            var inputLength = TFTensor.FromBuffer(new TFShape(boards.Length, 90), lengthBuffer, 0, lengthBuffer.Length);
            var inputScore = TFTensor.FromBuffer(new TFShape(boards.Length), new float[] { 100 }, 0, 1);
            return Predict(inputSquare, inputLength, inputScore);
        }

        private float[] Predict(TFTensor inputSquare, TFTensor inputLength, TFTensor inputBasicScore)
        {
            var runner = session.GetRunner();
            runner.AddInput("Model/input/input_square", inputSquare);
            runner.AddInput("Model/input/input_length", inputLength);
            runner.AddInput("Model/input/input_basic_score", inputBasicScore);
            runner.AddTarget("Model/score/score");
            var results = runner.Fetch("Model/score/score").Run();
            var scores = results[0].GetValue() as float[];
            return scores;
        }
    }
}
