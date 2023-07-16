import logging
import sys
from pathlib import Path

from tqdm import tqdm

from entity.image_container import ImageContainer
from entity.image_processor import ProcessorChain
from enums.constant import DEBUG
from init import MARGIN_PROCESSOR
from init import PADDING_TO_ORIGINAL_RATIO_PROCESSOR
from init import SEPARATE_LINE
from init import SHADOW_PROCESSOR
from init import SIMPLE_PROCESSOR
from init import config
from init import layout_items_dict
from init import root_menu
from utils import ENCODING
from utils import get_file_list


def processing():
    """
    状态100:处理图片
    :return:
    """
    # global state

    file_list = get_file_list(config.get_input_dir())[:2]
    print('当前共有 {} 张图片待处理'.format(len(file_list)))

    processor_chain = ProcessorChain()

    # 如果需要添加阴影,则添加阴影处理器,阴影处理器优先级最高,但是正方形布局不需要阴影
    if config.has_shadow_enabled() and 'square' != config.get_layout_type():
        processor_chain.add(SHADOW_PROCESSOR)

    # 根据布局添加不同的水印处理器
    if config.get_layout_type() in layout_items_dict:
        processor_chain.add(layout_items_dict.get(config.get_layout_type()).processor)
    else:
        processor_chain.add(SIMPLE_PROCESSOR)

    # 如果需要添加白边,且是水印布局,则添加白边处理器,白边处理器优先级最低
    if config.has_white_margin_enabled() and 'watermark' in config.get_layout_type():
        processor_chain.add(MARGIN_PROCESSOR)

    # 如果需要按原有比例填充,且不是正方形布局,则添加填充处理器
    if config.has_padding_with_original_ratio_enabled() and 'square' != config.get_layout_type():
        processor_chain.add(PADDING_TO_ORIGINAL_RATIO_PROCESSOR)

    for source_path in tqdm(file_list):
        # 打开图片
        container = ImageContainer(source_path)

        # 使用等效焦距
        container.is_use_equivalent_focal_length(config.use_equivalent_focal_length())

        # 处理图片
        try:
            processor_chain.process(container)
        except Exception as e:
            logging.exception(f'Error: {str(e)}')
            if DEBUG:
                raise e

        # 保存图片
        target_path = Path(config.get_output_dir(), encoding=ENCODING).joinpath(source_path.name)

        container.save(target_path, quality=config.get_quality())
        container.close()
    print('处理完成,文件已输出至 output 文件夹中,请点击任意键退出或直接关闭')
    # if DEBUG:
    #     sys.exit(0)
    # else:
    #     input()
    #     state = -1


# 0:主菜单,100:处理图片,-1:退出程序,其他:子菜单
# state = 100
# current_menu = root_menu
# root_menu.set_parent(root_menu)

if __name__ == '__main__':
    # Processing the image in the input folder directly
    processing(); config.save()
