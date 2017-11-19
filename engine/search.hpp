#pragma once
#include "rule.hpp"
#include <custom/compact_archive.hpp>
#include <fstream>
#include <unordered_map>
#include <filesystem>
#include <array>
#include <random>
#include <limits>
#include <optional>
#include <chrono>
#include <ctime>
#include <iostream>
namespace fs = std::experimental::filesystem;

class search_t
{
public:
	struct hash_item_t
	{
		int depth;
		int score;
		std::pair<int, int> move;
		DECLARE_SERIALIZE(depth, score, move)
	};

	struct search_item_t
	{
		std::string board;
		std::pair<int, int> move;
		int score;
	};

private:
	std::unordered_map<int64_t, hash_item_t> _hash;
	std::vector<std::unordered_map<char, int64_t>> _hash_table;
	int64_t _hit_count = 0;
	int64_t _save_count = 0;
	std::chrono::system_clock::time_point _start_time = std::chrono::system_clock::now();
public:
	search_t()
	{
		load();
	}

	void save()
	{
		std::ofstream file("hash.sav");
		auto ar = make_compact_archive(file);
		ar << _hash;
		ar << _hash_table;
		file.close();
	}

	std::vector<search_item_t> search(const std::string& board, bool red, int depth)
	{
		std::vector<search_item_t> r;
		deep_search(r, depth, board, red, depth, -rule_t::gameover_threshold() * 3, rule_t::gameover_threshold() * 3);
		std::stable_sort(r.begin(), r.end(), [red](const search_item_t& r0, const search_item_t& r1)
		{
			return red ? (r0.score > r1.score) : (r0.score < r1.score);
		});
		return r;
	}

	void get_hash_counter(int64_t& hit_count, int64_t& hash_size)
	{
		hit_count = _hit_count;
		hash_size = _hash.size();
	}
private:
	int deep_search(std::vector<search_item_t>& pack, int org_depth, const std::string& board, bool red, int depth, int minscore, int maxscore)
	{
		auto key = compute_hash(board, red);
		auto hash = find_hash(key);
		if (hash.has_value() && hash->depth >= depth)
		{
			if (depth == org_depth)
				fill_moves(pack, board, hash->move, hash->score, red);
			return hash->score;
		}

		auto moves = move_t::next_steps(board, red);
		std::vector<std::string> next_boards;
		std::vector<int> next_scores;

		std::pair<int, int> best_move;
		int best_score = red ? -rule_t::gameover_threshold() * 3 : rule_t::gameover_threshold() * 3;

		for (auto& move : moves)
		{
			auto next_board = move_t::next_board(board, move);
			auto next_score = rule_t::basic_score(next_board);
			if (red && next_score > best_score || !red && next_score < best_score)
			{
				best_move = move;
				best_score = next_score;
			}
			next_boards.push_back(next_board);
			next_scores.push_back(next_score);
		}
		if (1 == depth || abs(best_score) >= rule_t::gameover_threshold())
		{
			if (abs(best_score) >= rule_t::gameover_threshold())
			{
				if (best_score < 0)
					best_score -= depth;
				else
					best_score += depth;
			}
			if (depth == org_depth)
				fill_moves(pack, board, best_move, best_score, red);
			save_hash(key, depth, best_score, best_move);
			return best_score;
		}
		std::vector<int> idx(next_scores.size());
		for (int k = 0; k < (int)idx.size(); ++k)
			idx[k] = k;

		std::stable_sort(idx.begin(), idx.end(), [&](int i, int j)
		{
			return red ? (next_scores[i] > next_scores[j]) : (next_scores[i] < next_scores[j]);
		});
		best_score = red ? -rule_t::gameover_threshold() * 3 : rule_t::gameover_threshold() * 3;
		for (auto index : idx)
		{
			auto move = moves[index];
			auto board = next_boards[index];
			auto next_score = deep_search(pack, org_depth, board, !red, depth - 1, minscore, maxscore);
			if (red && next_score > best_score || !red && next_score < best_score)
			{
				best_score = next_score;
				best_move = move;
			}
			if (red)
			{
				if (next_score >= maxscore)
					break;
				else if (minscore < next_score)
					minscore = next_score;
			}
			else
			{
				if (next_score <= minscore)
					break;
				else if (maxscore > next_score)
					maxscore = next_score;
			}
			if (depth == org_depth)
				pack.push_back(search_item_t{ board, move, next_score });
		}
		save_hash(key, depth, best_score, best_move);
		return best_score;
	}

	void load()
	{
		if (fs::exists("hash.sav"))
		{
			std::ifstream file("hash.sav");
			auto ar = make_compact_archive(file);
			ar >> _hash;
			ar >> _hash_table;
			file.close();
		}
		else
		{
			auto types = rule_t::chess_types();
			types.push_back(' ');
			std::default_random_engine generator;
			std::uniform_int_distribution<int64_t> distribution;
			for (auto k = 0; k < 90; ++k)
			{
				std::unordered_map<char, int64_t> table;
				for (auto type : types)
				{
					table[type] = distribution(generator);
				}
				_hash_table.push_back(table);
			}
		}
	}

	int64_t compute_hash(const std::string& board, bool red)
	{
		int64_t hash = red ? 0 : -1;
		for (int k = 0; k < 90; ++k)
		{
			auto& table = _hash_table[k];
			hash ^= table[board[k]];
		}
		return hash;
	}

	std::optional<hash_item_t> find_hash(int64_t key)
	{
		auto itr = _hash.find(key);
		if (_hash.end() == itr)
			return std::optional<hash_item_t>();
		else
		{
			++_hit_count;
			return itr->second;
		}
	}

	void save_hash(int64_t key, int depth, int score, std::pair<int, int> move)
	{
		_hash[key] = hash_item_t{ depth, score, move };
		if (++_save_count % 100000 == 0)
		{
			auto now = std::chrono::system_clock::now();
			std::chrono::duration<double> duration = now - _start_time;
			if (duration.count() >= 60)
			{
				//save();
				_start_time = now;
			}
		}
	}

	void fill_moves(std::vector<search_item_t>& pack, const std::string& board, const std::pair<int, int>& move, int score, bool red)
	{
		if (pack.empty() == false)
			return;
		auto moves = move_t::next_steps(board, red);
		auto it = std::find(moves.begin(), moves.end(), move);
		std::swap(*moves.begin(), *it);
		for (auto& move : moves)
		{
			auto b = move_t::next_board(board, move);
			if (pack.empty() == false)
				score = rule_t::basic_score(b);
			pack.push_back(search_item_t{ b, move, score });
		}
	}
};