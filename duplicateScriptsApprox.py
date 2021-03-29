
from difflib import SequenceMatcher
import json
#import zipfile
import sys

N_BLOCKS = 6

LOOP_BLOCKS = ["control_repeat", "control_forever", "control_if", "control_if_else", "control_repeat_until"]


def find_dups(blocks):
    """
    Given blocks, which is a list of sequences of blocks
    Returns those subsequences that are duplicated
    """
    return_list = []
    for i in range(len(blocks)):
        for j in range(i + 1, len(blocks)):
            s = SequenceMatcher(None, blocks[i], blocks[j])
            match = s.find_longest_match(0, len(blocks[i]), 0, len(blocks[j]))
            if match.size >= N_BLOCKS:
                return_list.append(blocks[i][match.a:match.a + match.size])
    return return_list


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
        if filename.endswith(".zip"):
            zip_file = zipfile.ZipFile(filename, "r")
            json_project = json.loads(zip_file.open("project.json").read())
        elif filename.endswith(".json"):
            json_project = json.loads(open(filename).read())

        scripts_dict = {}

        # Loops through all sprites
        for sprites_dict in json_project["targets"]:
            sprite = sprites_dict["name"]
            blocks_dict = {}
            scripts_dict[sprite] = []

            # Gets all blocks out of sprite
            for blocks, blocks_value in sprites_dict["blocks"].items():
                if isinstance(blocks_value, dict):
                    blocks_dict[blocks] = blocks_value

            opcode_dict = {}   # block id -> opcode
            toplevel_list = []  # list of top-level block ids
            tmp_blocks = []
            for block_id, block in blocks_dict.items():
                opcode_dict[block_id] = block["opcode"]
                if block["topLevel"]:
                    if tmp_blocks:
                        scripts_dict[sprite].append(tmp_blocks)
                    toplevel_list.append(block_id)
                    tmp_blocks = [block["opcode"]]
                else:
                    tmp_blocks.append(block["opcode"])
            scripts_dict[sprite].append(tmp_blocks)
            # print(scripts_dict)

        # Intra-sprite
        self.intra_dups_list = []
        for sprite in scripts_dict:
            blocks = scripts_dict[sprite]
            dups = find_dups(blocks)
            if dups:
                self.intra_dups_list.append(dups[0])

        # Project-wide
        self.project_dups_list = []
        blocks = []
        for sprite in scripts_dict:
            blocks += scripts_dict[sprite]
        self.project_dups_list = find_dups(blocks)

    def finalize(self, filename):
        """Output the duplicate scripts detected."""
        with open(filename.replace('.json', '') + '-sprite.json', 'w') as outfile:
            json.dump(self.intra_dups_list, outfile)
        with open(filename.replace('.json', '') + '-project.json', 'w') as outfile:
            json.dump(self.project_dups_list, outfile)

#        count = sum([len(listElem) for listElem in self.intra_dups_list])
        count = len(self.intra_dups_list)
        result = ("{} intra-sprite duplicate scripts found\n".format(count))
        result += ("%d project-wide duplicate scripts found\n" % len(self.project_dups_list))

        return result


def main(filename):
    """The entrypoint for the 'duplicateScripts' extension"""
    duplicate = DuplicateScripts()
    print("Looking for duplicate scripts in", filename)
    print("Minimum number of blocks:", N_BLOCKS)
    print()
    duplicate.analyze(filename)
    print(duplicate.finalize(filename))

if __name__ == "__main__":
    main(sys.argv[1])
