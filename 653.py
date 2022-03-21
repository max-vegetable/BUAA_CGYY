# 这种两数之和，基本最坏情况都得O(n)，所以做的时候不要太畏手畏脚
# DFS+哈希
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def __init__(self):
        self.nums = set()

    def findTarget(self, root: Optional[TreeNode], k: int) -> bool:
        if root is None: # 注意这个条件必须有，否则会报错NoneType obj没有val
            return False
        if k - root.val in self.nums:
            return True
        self.nums.add(root.val)
        return self.findTarget(root.left, k) or self.findTarget(root.right, k)