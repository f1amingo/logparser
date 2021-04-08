N = int(input())
graph = [[0] * N for _ in range(N)]
nameIdx = {}
this_idx = 0
for _ in range(N):
    name1, name2 = input().split()
    if name1 not in nameIdx:
        nameIdx[name1] = this_idx
        this_idx += 1
    if name2 not in nameIdx:
        nameIdx[name2] = this_idx
        this_idx += 1
    i, j = nameIdx[name1], nameIdx[name2]
    graph[i][j] = graph[j][i] = 1

visit = set()
queue = []


def dfs(start: int):
    if start not in visit:
        visit.add(start)
        for j in range(N):
            if graph[start][j] == 1 and j not in visit:
                dfs(j)


ans = 0
for i in range(N):
    if i not in visit:
        dfs(i)
        ans += 1
print(ans)
