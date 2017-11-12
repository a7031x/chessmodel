#pragma once
#include <vector>
#include <ctype.h>
#include <tuple>
#include <set>

const int BASE = 100;
const int GAMEOVER_THRESHOLD = 500 * BASE;

class move_t
{
public:
	std::vector<std::pair<int, int>> next_steps(const std::string& board, bool red)
	{
		std::vector<std::pair<int, int>> steps;
		for (size_t k = 0; k < board.size(); ++k)
		{
			auto chess = board[k];
			if (side(chess) == 0 || is_red(chess) != red)
				continue;
			std::vector<int> moves;
			switch (toupper(chess))
			{
			case 'R':
				moves = rider_steps(board, k);
				break;
			case 'H':
				moves = horse_steps(board, k);
				break;
			case 'E':
				moves = elephant_steps(board, k);
				break;
			case 'B':
				moves = bishop_steps(board, k);
				break;
			case 'K':
				moves = king_steps(board, k);
				break;
			case 'C':
				moves = cannon_steps(board, k);
				break;
			case 'P':
				moves = pawn_steps(board, k);
				break;
			default:
				throw std::exception("invalid chess");
				break;
			}
			for (auto move : moves)
				steps.push_back(std::pair<int, int>((int)k, move));
		}
		return steps;
	}
private:
	std::vector<int> rider_steps(const std::string& board, int pos)
	{
		std::vector<int> steps;
		int px, py;
		std::tie(px, py) = position2(pos);
		auto check_add = [&](int x, int y)
		{
			auto p = position1(x, y);
			if (side(board[p]) * side(board[pos]) <= 0)
				steps.push_back(p);
			return ' ' == board[p];
		};

		for (int x = px + 1; x < 9 && check_add(x, py); ++x);
		for (int x = px - 1; x >= 0 && check_add(x, py); --x);
		for (int y = py + 1; y < 10 && check_add(px, y); ++y);
		for (int y = py - 1; y >= 0 && check_add(px, y); --y);

		return steps;
	}

	std::vector<int> horse_steps(const std::string& board, int pos)
	{
		std::vector<int> steps;
		int px, py;
		std::tie(px, py) = position2(pos);

		const int dx[] = { -2, -2, 2, 2, -1, -1, 1, 1 };
		const int dy[] = { -1, 1, -1, 1, -2, 2, -2, 2 };

		for (int k = 0; k < 8; ++k)
		{
			if (false == valid_position(px + dx[k], py + dy[k]))
				continue;
			auto bx = dx[k] / 2;
			auto by = dy[k] / 2;
			if (board[position1(px + bx, py + by)] != ' ')
				continue;
			auto p = position1(px + dx[k], py + dy[k]);
			if (side(board[p]) * side(board[pos]) <= 0)
				steps.push_back(p);
		}
		return steps;
	}

	std::vector<int> elephant_steps(const std::string& board, int pos)
	{
		std::vector<int> steps;
		int px, py;
		std::tie(px, py) = position2(pos);

		const int dx[] = { -2, 2, -2, 2 };
		const int dy[] = { -2, -2, 2, 2 };
		static std::set<int> valid_py = { 0, 2, 4, 5, 7, 9 };
		for (int k = 0; k < 4; ++k)
		{
			if (false == valid_position(px + dx[k], py + dy[k]))
				continue;
			auto bx = dx[k] / 2;
			auto by = dy[k] / 2;
			if (board[position1(px + bx, py + by)] != ' ')
				continue;
			if (valid_py.end() == valid_py.find(py + dy[k]))
				continue;
			auto p = position1(px + dx[k], py + dy[k]);
			if (side(board[p]) * side(board[pos]) <= 0)
				steps.push_back(p);
		}
		return steps;
	}

private:
	inline bool is_red(char chess)
	{
		return 'A' <= chess && 'Z' >= chess;
	}


	inline int position1(int x, int y)
	{
		return x + y * 9;
	}


	inline std::pair<int, int> position2(int pos)
	{
		return std::pair<int, int>(pos % 9, pos / 9);
	}

	inline int side(char chess)
	{
		if (is_red(chess))
			return 1;
		else if (' ' == chess)
			return 0;
		else
			return -1;
	}

	inline int valid_position(int x, int y)
	{
		return x >= 0 && x < 9 && y >= 0 && y < 10;
	}
};

