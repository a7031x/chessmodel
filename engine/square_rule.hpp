#pragma once
#include <array>
#include <vector>
#include <string>
#include "rule.hpp"

class square_rule_t
{
public:
	struct chess_state_t
	{
		char piece;
		int state;
	};
public:
	static std::array<std::vector<chess_state_t>, 90> square_map(const std::string& board)
	{
		std::array<std::vector<chess_state_t>, 90> map;

		for (int k = 0; k < 90; ++k)
		{
			auto piece = board[k];
			if (rule_t::side(piece) == 0)
				continue;
			map[k].push_back({ piece, 0 });
			auto states = next_covers(board, k);
			int state = 1;
			for (auto& s : states)
			{
				for (auto pos : s)
					map[pos].push_back({ piece, state });
				++state;
			}
		}
		return map;
	}

private:
	typedef std::vector<std::vector<int>> states_t;

	static states_t next_covers(const std::string& board, int pos)
	{
		auto piece = board[pos];
		switch (toupper(piece))
		{
		case 'R':
			return next_rider_covers(board, pos);
		case 'N':
			return next_horse_covers(board, pos);
		case 'B':
			return next_elephant_covers(board, pos);
		case 'A':
			return next_bishop_covers(board, pos);
		case 'K':
			return next_king_covers(board, pos);
		case 'C':
			return next_cannon_covers(board, pos);
		case 'P':
			return next_pawn_covers(board, pos);
		}
	}

	static states_t next_rider_covers(const std::string& board, int pos)
	{
		std::vector<int> covers;
		std::vector<int> next;
		int counter = 0;
		int px, py;
		std::tie(px, py) = rule_t::position2(pos);
		auto check_add = [&counter, &covers, &next, &board](int x, int y)
		{
			auto pos = rule_t::position1(x, y);
			if (0 == counter)
				covers.push_back(pos);
			else if (1 == counter)
				next.push_back(pos);
			if (' ' != board[pos])
			{
				if (++counter == 2)
					return false;
			}
			return true;
		};
		for (int x = px + 1; x < 9 && check_add(x, py); ++x);
		counter = 0;
		for (int x = px - 1; x >= 0 && check_add(x, py); --x);
		counter = 0;
		for (int y = py + 1; y < 10 && check_add(px, y); ++y);
		counter = 0;
		for (int y = py - 1; y >= 0 && check_add(px, y); --y);
		return { covers, next };
	}

	static states_t next_horse_covers(const std::string& board, int pos)
	{
		std::vector<int> steps, blocks, next;
		int px, py;
		std::tie(px, py) = rule_t::position2(pos);
		const int dx[] = { -2, -2, 2, 2, -1, -1, 1, 1 };
		const int dy[] = { -1, 1, -1, 1, -2, 2, -2, 2 };
		for (int k = 0; k < 8; ++k)
		{
			if (false == rule_t::valid_position(px + dx[k], py + dy[k]))
				continue;
			auto bx = dx[k] / 2;
			auto by = dy[k] / 2;
			auto block_position = rule_t::position1(px + bx, py + by);
			auto block = board[block_position] != ' ';
			auto pos = rule_t::position1(px + dx[k], px + dy[k]);
			if (block)
			{
				blocks.push_back(block_position);
				next.push_back(pos);
			}
			else
				steps.push_back(pos);
		}
		return { steps, blocks, next };
	}

	static states_t next_elephant_covers(const std::string& board, int pos)
	{
		std::vector<int> steps, blocks, next;
		int px, py;
		std::tie(px, py) = rule_t::position2(pos);
		const int dx[] = { -2, 2, -2, 2 };
		const int dy[] = { -2, -2, 2, 2 };
		static std::set<int> valid_py = { 0, 2, 4, 5, 7, 9 };
		for (int k = 0; k < 4; ++k)
		{
			if (false == rule_t::valid_position(px + dx[k], py + dy[k]))
				continue;
			if (valid_py.end() == valid_py.find(py + dy[k]))
				continue;
			auto bx = dx[k] / 2;
			auto by = dy[k] / 2;
			auto block_position = rule_t::position1(px + bx, py + by);
			auto block = board[block_position] != ' ';
			auto pos = rule_t::position1(px + dx[k], px + dy[k]);
			if (block)
			{
				blocks.push_back(block_position);
				next.push_back(pos);
			}
			else
				steps.push_back(pos);
		}
		return { steps, blocks, next };
	}

	static states_t next_bishop_covers(const std::string& board, int pos)
	{
		std::vector<int> steps;
		int px, py;
		std::tie(px, py) = rule_t::position2(pos);
		const int dx[] = { -1, 1, -1, 1 };
		const int dy[] = { -1, -1, 1, 1 };
		static std::set<int> valid_py = { 0, 1, 2, 7, 8, 9 };
		for (int k = 0; k < 4; ++k)
		{
			if (false == valid_position(px + dx[k], py + dy[k]))
				continue;
			if (px + dx[k] < 3 || px + dx[k] > 5 || valid_py.end() == valid_py.find(py + dy[k]))
				continue;
			auto p = position1(px + dx[k], py + dy[k]);
			steps.push_back(p);
		}
		return { steps };
	}

	static states_t next_king_covers(const std::string& board, int pos)
	{
		std::vector<int> steps, check;
		int px, py;
		std::tie(px, py) = rule_t::position2(pos);
		const int dx[] = { -1, 1, 0, 0 };
		const int dy[] = { 0, 0, -1, 1 };
		static std::set<int> valid_py = { 0, 1, 2, 7, 8, 9 };

		for (int k = 0; k < 4; ++k)
		{
			if (false == rule_t::valid_position(px + dx[k], py + dy[k]))
				continue;
			if (px + dx[k] < 3 || px + dx[k] > 5 || valid_py.end() == valid_py.find(py + dy[k]))
				continue;
			auto p = rule_t::position1(px + dx[k], py + dy[k]);
			steps.push_back(p);
		}
		auto inc = py <= 2 ? 1 : -1;
		for (int y = py + inc; y >= 0 && y < 10; y += inc)
		{
			auto p = rule_t::position1(px, y);
			if (' ' != board[p])
			{
				if ('K' == toupper(board[p]))
					steps.push_back(p);
				break;
			}
			else
			{
				if (py <= 2 && y >= 7 || py >= 7 && y <= 2)
					check.push_back(p);
			}
		}
		return { steps, check };
	}

	static states_t next_cannon_covers(const std::string& board, int pos)
	{
		std::vector<int> steps, next;
		int px, py;
		std::tie(px, py) = rule_t::position2(pos);

		int counter = 0;
		auto check_add = [&steps, &next, &counter, &board](int x, int y)
		{
			auto p = rule_t::position1(x, y);
			if (1 == counter)
				steps.push_back(p);
			else if (2 == counter)
				next.push_back(p);
			if (' ' != board[p])
			{
				if (++counter == 3)
					return false;
			}
			return true;
		};
		for (int x = px + 1; x < 9 && check_add(x, py); ++x);
		counter = 0;
		for (int x = px - 1; x >= 0 && check_add(x, py); --x);
		counter = 0;
		for (int y = py + 1; y < 10 && check_add(px, y); ++y);
		counter = 0;
		for (int y = py - 1; y >= 0 && check_add(px, y); --y);
		return { steps, next };
	}

	static states_t next_pawn_covers(const std::string& board, int pos)
	{
		std::vector<int> steps;
		int px, py;
		std::tie(px, py) = rule_t::position2(pos);
		const int dx[] = { 0, -1, 1 };
		const int dy[] = { -1, 0, 0 };
		int reverse;
		int count;

		auto red_king_pos = (int)board.find_first_of('K', 0);
		if (is_red(board[pos]) == (red_king_pos >= 45))
		{
			if (py <= 4)
				count = 3;
			else
				count = 1;
			reverse = 1;
		}
		else
		{
			if (py >= 5)
				count = 3;
			else
				count = 1;
			reverse = -1;
		}

		for (int k = 0; k < count; ++k)
		{
			if (false == rule_t::valid_position(px + dx[k], py + dy[k] * reverse))
				continue;
			auto p = rule_t::position1(px + dx[k], py + dy[k] * reverse);
			steps.push_back(p);
		}
		return { steps };
	}
};