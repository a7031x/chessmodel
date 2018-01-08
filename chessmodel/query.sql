--select count(1) from board_score;
select
avg(score) as avg,
sqrt(avg(score*score) - avg(score)*avg(score)) stdv,
sum(expand) as expand,
count(1) - sum(expand) as expanding,
count(1) cnt
from board_score
where abs(score) <= 5000
--select * from board_score order by abs(score) desc