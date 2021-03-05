
import json
import zipfile

N_BLOCKS = 4

LOOP_BLOCKS = ["control_repeat", "control_forever", "control_if", "control_if_else", "control_repeat_until"]


class DuplicateScripts:
    """
    Analyzer of duplicate scripts in sb3 projects sb3
    New version for Scratch 3.0
    """

    def __init__(self):
        self.blocks_dict = {}
        self.total_blocks = []
        self.list_duplicate = []
        self.blocks_dup = {}
        #  self.list_duplicate_string = []

    def analyze(self, filename):
        """Only takes into account scripts with more than 5 blocks"""
        zip_file = zipfile.ZipFile(filename, "r")
        json_project = json.loads(zip_file.open("project.json").read())
  
        scripts_set = {}

        for key, value in json_project.items():
            print(key)
            if key == "targets":
                for dictionary in value:
                    sprite = dictionary["name"]
                    self.blocks_dict = {}
                    scripts_set[sprite] = []

                    for blocks, blocks_value in dictionary["blocks"].items():
                        # for blocks, blocks_value in dict_value.iteritems():
                        if isinstance(blocks_value, dict):
                            self.blocks_dict[blocks] = blocks_value
                            self.total_blocks.append(blocks_value)

                    for key_block in self.blocks_dict:
                        block = self.blocks_dict[key_block]

                        if block["topLevel"]:
                            block_list = []
                            next_block = block["next"]
                            aux_next = []
                            else_block = None
                            self.search_next(next_block, block_list, key_block, aux_next, else_block)

                            blocks_tuple = tuple(block_list)

                            for sprite_key, sprite_value in scripts_set.items():
                                if blocks_tuple in sprite_value:
                                    self.list_duplicate.append(block_list)

                            # Only save the scripts with more than N_BLOCKS blocks
                            if len(block_list) >= N_BLOCKS:
                                scripts_set[sprite].append(blocks_tuple)
        print(scripts_set)

        #  Find the number of duplicates
        for repeat_block in self.list_duplicate:
            sprites_dup = []

            for key, value in scripts_set.items():
                if tuple(repeat_block) in value:
                    sprites_dup.append(str(key))

            sprites_dup = ", ".join(sprites_dup)
            if sprites_dup not in self.blocks_dup:
                self.blocks_dup[sprites_dup] = []

            self.blocks_dup[sprites_dup].append(repeat_block)

    def search_next(self, next_block, block_list, key_block, aux_next, else_block):

        block = self.blocks_dict[key_block]
        block_list.append(block["opcode"])

        # Check if it's if_else block
        try:
            is_else = block["inputs"]["SUBSTACK2"][1]
        except KeyError:
            is_else = None

        if not next_block:
            # Maybe is a loop block
            try:
                next_block = self.blocks_dict[key_block]["inputs"]["SUBSTACK"][1]
            except KeyError:
                print("KeyError")
            if not next_block:
                block_list.append("finish_end")
                return

            block = self.blocks_dict[next_block]
            key_block = next_block
            next_block = block["next"]

            self.search_next(next_block, block_list, key_block, aux_next, is_else)
            block_list.append("finish_end")

            if else_block:
                next_block = else_block
                else_block = None
                block_list.append("control_else")
            else:
                return
        else:
            # Maybe it is a loop block
            is_loop = any(self.blocks_dict[key_block]["opcode"] == loop for loop in LOOP_BLOCKS)
            if is_loop:
                loop_block = self.blocks_dict[key_block]["inputs"]["SUBSTACK"][1]
                aux_next.append(next_block)  # Add the real next until the end of the loop
                next_block = loop_block

                if next_block:
                    block = self.blocks_dict[next_block]
                    key_block = next_block
                    next_block = block["next"]
                    self.search_next(next_block, block_list, key_block, aux_next, is_else)

                    block_list.append("finish_end")
                    if aux_next:  # Check if there is an aux_next saved
                        next_block = aux_next[-1]
                        aux_next.pop(-1)
                    else:
                        return

        if next_block:
            block = self.blocks_dict[next_block]
            key_block = next_block
            next_block = block["next"]

            self.search_next(next_block, block_list, key_block, aux_next, else_block)

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
#    print(duplicate.finalize())


if __name__ == "__main__":
    my_path = "./projects/"
    new_path = "./sb3/"
    """only_files = [f for f in listdir(my_path) if isfile(join(my_path, f))]
    for file in only_files:
        main("./projects/" + file)"""
    main("test.sb3")
