import struct

class SuperBloque:
    def __init__(self):
        self.s_filesystem_type = 0
        self.s_inodes_count = 0
        self.s_blocks_count = 0
        self.s_free_blocks_count = 0
        self.s_free_inodes_count = 0
        self.s_mtime = 0
        self.s_umtime = 0
        self.s_mnt_count = 0
        self.s_magic = 0xEF53
        self.s_inode_size = 0
        self.s_block_size = 0
        self.s_first_ino = 0
        self.s_first_blo = 0
        self.s_bm_inode_start = 0
        self.s_bm_block_start = 0
        self.s_inode_start = 0
        self.s_block_start = 0

    def __bytes__(self):
        return (struct.pack("<i", self.s_filesystem_type) +
                struct.pack("<i", self.s_inodes_count) +
                struct.pack("<i", self.s_blocks_count) +
                struct.pack("<i", self.s_free_blocks_count) +
                struct.pack("<i", self.s_free_inodes_count) +
                struct.pack("<d", self.s_mtime) +
                struct.pack("<d", self.s_umtime) +
                struct.pack("<i", self.s_mnt_count) +
                struct.pack("<i", self.s_magic) +
                struct.pack("<i", self.s_inode_size) +
                struct.pack("<i", self.s_block_size) +
                struct.pack("<i", self.s_first_ino) +
                struct.pack("<i", self.s_first_blo) +
                struct.pack("<i", self.s_bm_inode_start) +
                struct.pack("<i", self.s_bm_block_start) +
                struct.pack("<i", self.s_inode_start) +
                struct.pack("<i", self.s_block_start))