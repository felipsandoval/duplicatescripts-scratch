
from difflib import SequenceMatcher
import json
import zipfile

N_BLOCKS = 5

LOOP_BLOCKS = ["control_repeat", "control_forever", "control_if", "control_if_else", "control_repeat_until"]


class DuplicateScripts:
    """
    Analyzer of duplicate scripts in sb3 projects sb3
    New version for Scratch 3.0
    """

    def __init__(self):
        #  self.blocks_dict = {}
        #  self.all_blocks = []
        self.list_duplicate = []
        self.blocks_dup = {}
        #  self.list_duplicate_string = []

    def analyze(self, filename):
        """TODO"""
        zip_file = zipfile.ZipFile(filename, "r")
        json_project = json.loads(zip_file.open("project.json").read())
  
        scripts_dict = {}

        # Loops through all sprites
        for sprites_dict in json_project["targets"]:
            sprite = sprites_dict["name"]
            self.blocks_dict = {}
            scripts_dict[sprite] = []

            # Gets all blocks out of sprite
            for blocks, blocks_value in sprites_dict["blocks"].items():
                if isinstance(blocks_value, dict):
                    self.blocks_dict[blocks] = blocks_value
                    #  self.all_blocks.append(blocks_value)
#            print(sprite, len(self.blocks_dict))
#            print(self.blocks_dict)

            opcode_dict = {}   # block id -> opcode
            topLevel_list = []  # list of top-level block ids
            tmp_blocks = []
            for block_id, block in self.blocks_dict.items():
                opcode_dict[block_id] = block["opcode"]
                if block["topLevel"]:
                    if tmp_blocks:
                        scripts_dict[sprite].append(tmp_blocks)
                    topLevel_list.append(block_id)
                    tmp_blocks = [block["opcode"]]
                else:
                    tmp_blocks.append(block["opcode"])
            scripts_dict[sprite].append(tmp_blocks)
            print(scripts_dict)

        # Intra
        for sprite in scripts_dict:
            blocks = scripts_dict[sprite]
            for i in range(len(blocks)):
                for j in range(i+1, len(blocks)):
#                    print(sprite, i, blocks[i], j, blocks[j])
                    s = SequenceMatcher(None, blocks[i], blocks[j])
                    match = s.find_longest_match(0, len(blocks[i]), 0, len(blocks[j]))
                    if match.size >= N_BLOCKS:
                        print(sprite, match.size, blocks[i][match.a:match.a+match.size])

        # Project-wide
        blocks = []
        for sprite in scripts_dict:
            blocks += scripts_dict[sprite]
        print(blocks)
        for i in range(len(blocks)):
            for j in range(i+1, len(blocks)):
#                print(sprite, i, blocks[i], j, blocks[j])
                s = SequenceMatcher(None, blocks[i], blocks[j])
                match = s.find_longest_match(0, len(blocks[i]), 0, len(blocks[j]))
                if match.size >= N_BLOCKS:
                    print(match.size, blocks[i][match.a:match.a+match.size])

#             # Looks for all scripts (i.e., sequence of blocks) in a sprite
#             for block_id, block in self.blocks_dict.items():
#                 if block["topLevel"]:
#                     block_list = self.search_next(block["next"], [], block_id, [], None)
#                     blocks_tuple = tuple(block_list)
#
#                     print(blocks_tuple)
#                     for sprite_key, sprite_value in scripts_dict.items():
#                         if blocks_tuple in sprite_value:
#                             self.list_duplicate.append(block_list)
#
#                     # Only save the scripts with more than N_BLOCKS blocks
#                     if len(block_list) >= N_BLOCKS:
#                         scripts_dict[sprite].append(blocks_tuple)
# #        print(scripts_dict)
#
#         #  Find the number of duplicates
#         for repeat_block in self.list_duplicate:
#             sprites_dup = []
#
#             for key, value in scripts_dict.items():
#                 if tuple(repeat_block) in value:
#                     sprites_dup.append(str(key))
#
#             sprites_dup = ", ".join(sprites_dup)
#             if sprites_dup not in self.blocks_dup:
#                 self.blocks_dup[sprites_dup] = []
#
#             self.blocks_dup[sprites_dup].append(repeat_block)
#
#     def search_next(self, next_block, block_list, block_id, aux_next, else_block):
#
#         block = self.blocks_dict[block_id]
#         block_list.append(block["opcode"])
#
#         # Check if it's if_else block
#         try:
#             is_else = block["inputs"]["SUBSTACK2"][1]
# #            is_else = block["inputs"].get("SUBSTACK2", None)
#         except KeyError:
#             is_else = None
#
#         if not next_block:
#             # Maybe it is a loop block
#             try:
#                 next_block = self.blocks_dict[block_id]["inputs"]["SUBSTACK"][1]
#             except KeyError:
#                 print("No next block")
#             if not next_block:
#                 block_list.append("finish_end")
#                 return block_list
#
#             block = self.blocks_dict[next_block]
#             block_id = next_block
#             next_block = block["next"]
#
#             block_list = self.search_next(next_block, block_list, block_id, aux_next, is_else)
#             block_list.append("finish_end")
#
#             if else_block:
#                 next_block = else_block
#                 else_block = None
#                 block_list.append("control_else")
#             else:
#                 return block_list
#         else:
#             # Maybe it is a loop block
#             is_loop = any(self.blocks_dict[block_id]["opcode"] == loop for loop in LOOP_BLOCKS)
#             if is_loop:
#                 loop_block = self.blocks_dict[block_id]["inputs"]["SUBSTACK"][1]
#                 aux_next.append(next_block)  # Add the real next until the end of the loop
#                 next_block = loop_block
#
#                 if next_block:
#                     block = self.blocks_dict[next_block]
#                     block_id = next_block
#                     next_block = block["next"]
#                     block_list = self.search_next(next_block, block_list, block_id, aux_next, is_else)
#
#                     block_list.append("finish_end")
#                     if aux_next:  # Check if there is an aux_next saved
#                         next_block = aux_next[-1]
#                         aux_next.pop(-1)
#                     else:
#                         return block_list
#
#         if next_block:
#             block = self.blocks_dict[next_block]
#             block_id = next_block
#             next_block = block["next"]
#
#             block_list = self.search_next(next_block, block_list, block_id, aux_next, else_block)
#         return block_list


    def finalize(self):
        """Output the duplicate scripts detected."""
        result = ("%d duplicate scripts found" % len(self.list_duplicate))
        result += "\n"
        result += str(self.blocks_dup)

        return result


def main(filename):
    """The entrypoint for the 'duplicateScripts' extension"""
    duplicate = DuplicateScripts()
    duplicate.analyze(filename)
#   print(duplicate.finalize())


if __name__ == "__main__":
    my_path = "./projects/"
    new_path = "./sb3/"
    """only_files = [f for f in listdir(my_path) if isfile(join(my_path, f))]
    for file in only_files:
        main("./projects/" + file)"""
    main("prueba.sb3")
