ENGLISH_PROMPT = """
    You are a creative story writer that creates engaging choose-your-own-adventure stories.
    Generate a complete branching story with multiple paths and endings in the JSON format I'll specify.

    The story should have:
    1. A compelling title
    2. A starting situation (root node) with 2 options
    3. Each option should lead to another node with its own options
    4. Some paths should lead to a winning ending

    Story structure requirements:
    - Each node should have 2 options except for ending nodes
    - The story should be 3-4 levels deep(including root node)
    - Add variety in the path lengths (some end earlier, some later)
    - Make sure there's at least one winning path

    Output your story in the exact JSON structure:
    {format_instructions}

    Don't simplify or omit part of the story structure.
    Don't add any text outside of the JSON structure.
"""

STORY_PROMPT = """
    你是一个创意故事作家，风格简洁精炼，创作引人入胜的choose-your-own-adventure故事。
    生成一套完整的树形故事，它有多条路径和结尾，以我给出的JSON格式返回。

    这个故事包含：
    1. 一个引人入胜的题目
    2. 一个拥有两个选项的开头（root node）
    3. 每个选项都关联另一个node，这个node又有自己的选项
    4. 这其中的一些路径应该通向胜利的结局
    5. 每个node文本尽量精简，无需细节描写，控制在30字以内

    故事结构要求：
    - 除了结束node每个node应该有2个选项
    - 故事路径应该有3-4层深
    - 保证至少有一个胜利结局

    用精确的JSON结构输出你的故事：
    {format_instructions}

    不要简化或忽略故事结构的任一部分。
    不要在JSON结构外部添加任何文本。
"""

json_structure = """
    {
        "title": "Story Title",
        "rootNode": {
            "content": "the starting situation of the story",
            "idEnding": false,
            "isWinningEnding": false,
            "options": [
                {
                    "text": "Option 1 text",
                    "nextNode": {
                        "content": "What heppens for option 1",
                        "isEnding": false,
                        "isWinningEnding": false,
                        "options": [
                            // More nested options
                        ]
                    }
                },
                // More options for root node
            ] 
        } 
    }
"""