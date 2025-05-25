from NitroTools.FileSystem import EndianBinaryReader
from NitroTools.FileResource import File
from PIL import Image
import os

class JitenAnimation(File):
    def read(self, f : EndianBinaryReader):
        f.check_magic(b"\x21\x03\x00\x40")
        self.distinct_frame_count = f.read_UInt16()
        self.frame_count = f.read_UInt16()
        self.frames_info = [FrameInfo(f) for _ in range(self.frame_count)]
        self.distinct_frames = [Frame(f) for _ in range(self.distinct_frame_count)]

    def export_frames(self,images: list[Image.Image],output_path : str):
        for idx, frame in enumerate(self.distinct_frames):
            im = frame.export_frame(images)
            im.save(os.path.join(output_path,f"{idx}.png"))

    def export_gif(self, images: list[Image.Image],output_path):
        frames_im = [frame.export_frame(images) for frame in self.distinct_frames]
        frames = [frames_im[frame_info.frame_idx] for frame_info in self.frames_info[:-1]]
        duration = [frame_info.duration * (1000 / 60) for frame_info in self.frames_info[:-1]]
        frames[0].save(output_path,save_all=True, append_images = frames[1:], loop = 0, duration = duration,disposal = 2)


class FrameInfo:
    def __init__(self,f : EndianBinaryReader):
        self.frame_idx = f.read_UInt16()
        self.duration = f.read_UInt16()
        self.padding = f.read_Int32() # ?


class Frame:
    def __init__(self,f : EndianBinaryReader):
        self.region_count = f.read_Int32()
        self.regions = [FrameRegion(f) for _ in range(self.region_count)]

    def export_frame(self,images: list[Image.Image]):
        frame_im = Image.new('RGBA',(256,256))
        for region in self.regions:
            region_im = images[region.pal_idx].crop((region.source_upleft_x_coord,region.source_upleft_y_coord,region.source_upleft_x_coord + region.source_width,region.source_upleft_y_coord + region.source_height))
            if region.mirror_flag:
                region_im = region_im.transpose(Image.FLIP_LEFT_RIGHT)
            frame_im.alpha_composite(region_im,(region.dest_upleft_x_coord,region.dest_upleft_y_coord))
        return frame_im

class FrameRegion:
    def __init__(self, f : EndianBinaryReader):
        self.source_upleft_x_coord = f.read_UInt8()
        self.source_upleft_y_coord = f.read_UInt8()
        self.dest_upleft_x_coord = f.read_UInt8()
        self.dest_upleft_y_coord = f.read_UInt8()
        self.pal_idx = f.read_UInt8() // 0x40
        self.unk = f.read_UInt16()
        self.flag = f.read_UInt8()
        if self.flag < 0x10:
            self.source_width = f.read_UInt16()
            self.source_height = f.read_UInt16()
        else:
            self.source_width = self.source_height = self.flag // 2
        self.mirror_flag =  (self.flag % 0x10 == 4)
        self.unk1 = f.read_UInt16()
        self.unk2 = f.read_UInt16()
        self.unk3 = f.read_UInt16()
        self.unk4 = f.read_UInt16()