#include "model.h"
#include "square_rule.hpp"
#include <vector>
#include <tensorflow/cc/saved_model/loader.h>
#include <tensorflow/cc/client/client_session.h>
#include <tensorflow/cc/ops/standard_ops.h>
#include <tensorflow/core/framework/tensor.h>

class model_imply : model_t
{
public:
	model_imply() : piece_to_id(
		{ {'R', 0}, {'N', 1}, {'B', 2}, {'A', 3}, {'K', 4}, {'C', 5}, {'P', 6},
		{'r', 7}, {'n', 8}, {'b', 9}, {'a', 10}, {'k', 11}, {'c', 12}, {'p', 13} })
	{
		_bundle = std::make_shared<tensorflow::SavedModelBundle>();
		auto status = tensorflow::LoadSavedModel(tensorflow::SessionOptions(), tensorflow::RunOptions(), "./model/1.4", { "serve" }, &*_bundle);
		assert(status.ok());
	}

	std::vector<float> predict(const std::vector<std::string> &boards, bool red) override
	{
		std::vector<square_rule_t::square_map_t> maps, feed_maps;
		std::vector<int> scores;
		for (auto& board : boards)
		{
			square_rule_t::square_map_t map;
			int score;
			std::tie(map, score) = normalized_map_and_score(board, red);
			maps.push_back(map);
			scores.push_back(score);
		}

		auto batch_size = (int)boards.size();
		std::vector<std::array<int, 90>> length;
		int mlen = 0;
		for (auto& map : maps)
		{
			std::array<int, 90> x;
			for (int k = 0; k < 90; ++k)
				x[k] = map[k].size();
			mlen = std::max((int)*std::max_element(x.begin(), x.end()), mlen);
			length.push_back(x);
		}

		for (auto& map : maps)
		{
			square_rule_t::square_map_t feed_map;
			for (int k = 0; k < 90; ++k)
			{
				feed_map[k] = create_feed_row(map[k], mlen);
			}
			feed_maps.push_back(feed_map);
		}
	}

private:
	std::vector<square_rule_t::chess_state_t> create_feed_row(const std::vector<square_rule_t::chess_state_t>& row, int mlen)
	{
		std::vector<square_rule_t::chess_state_t> feed_row;
		for (auto& state : row)
		{
			auto state2 = state;
			state2.piece = piece_to_id[state.piece];
			feed_row.push_back(state2);
		}
		for (auto k = feed_row.size(); k < size_t(mlen); ++k)
		{
			feed_row.push_back({ 14, 0 });
		}
		return feed_row;
	}

	std::pair<square_rule_t::square_map_t, int> normalized_map_and_score(const std::string& board, bool red)
	{
		auto board = normalize_board(board, red);
		return std::make_pair(square_rule_t::square_map(board), rule_t::basic_score(board));
	}

	std::string normalize_board(const std::string& board, bool red)
	{
		std::string r;
		if (false == red)
		{
			for (auto piece : board)
				r += rule_t::flip_side(piece);
		}
		else
			r = board;
		if (board.find('K', 0) < 45)
			return rule_t::rotate_board(r);
		else
			return r;
	}

private:
	std::shared_ptr<tensorflow::SavedModelBundle> _bundle;
	std::unordered_map<char, int> piece_to_id;
};

std::shared_ptr<model_t> model_t::create()
{
	return std::static_pointer_cast<model_t, model_imply>(std::make_shared<model_imply>());
}
