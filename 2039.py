class Solution:
    def networkBecomesIdle(self, edges: List[List[int]], patience: List[int]) -> int:
        # 这个距离公式有时间再推一下
        # 建图
        n = len(patience)
        G = [[] for _ in range(n)] # 邻接表
        for (u, v) in edges:
            G[u].append(v)
            G[v].append(u)
        
        vis = [False] * n
        q = deque([0])
        vis[0] = True
        ans, dis = 0, 1
        while q:
            for _ in range(len(q)): # 注意这里很精髓啊，看似无用，实际对应了dis必须是BFS逐层+1
                vertex = q.popleft()
                for i in G[vertex]:
                    if vis[i] is True:
                        continue
                    vis[i] = True
                    q.append(i)
                    ans = max(ans, (dis*2-1) // patience[i] * patience[i] + dis*2 + 1)
            dis += 1
        return ans
