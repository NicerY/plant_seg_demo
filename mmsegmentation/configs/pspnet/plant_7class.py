_base_ = [
    '../_base_/default_runtime.py'
]

# # Model config
norm_cfg = dict(type='SyncBN', requires_grad=True)
model = dict(
    type='EncoderDecoder',
    pretrained='open-mmlab://resnet50_v1c',
    backbone=dict(
        type='ResNetV1c',
        depth=50,
        num_stages=4,
        out_indices=(0, 1, 2, 3),
        dilations=(1, 1, 2, 4),
        strides=(1, 2, 1, 1),
        norm_cfg=norm_cfg,
        norm_eval=False,
        style='pytorch',
        contract_dilation=True),
    decode_head=dict(
        type='PSPHead',
        in_channels=2048,
        in_index=3,
        channels=512,
        pool_scales=(1, 2, 3, 6),
        dropout_ratio=0.1,
        num_classes=7,
        norm_cfg=norm_cfg,
        align_corners=False,
        loss_decode=dict(
            type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0)),
    auxiliary_head=dict(
        type='FCNHead',
        in_channels=1024,
        in_index=2,
        channels=256,
        num_convs=1,
        concat_input=False,
        dropout_ratio=0.1,
        num_classes=7,
        norm_cfg=norm_cfg,
        align_corners=False,
        loss_decode=dict(
            type='CrossEntropyLoss', use_sigmoid=False, loss_weight=0.4)),
    train_cfg=dict(),
    test_cfg=dict(mode='whole'))
     
    #这个mode='whole'必须写
    #'whole代表全图推理模式',
    #滑窗重叠预测可修改为：test_cfg=dict(mode='slide', crop_size=crop_size, stride=(341, 341))


# Dataset config
img_norm_cfg = dict(
    mean=[123.675, 116.28, 103.53],  
    std=[58.395, 57.12, 57.375], 
    to_rgb=True)


train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='LoadAnnotations'),
    dict(type='Resize', img_scale=(1000, 750)),
    dict(type='RandomFlip', prob=0.5, direction='horizontal'),#这里改了,必须有RandomFlip，但可以为0
    dict(type='Normalize', **img_norm_cfg),
    dict(type='DefaultFormatBundle'),#这里好像必须写DefaultFormatBundle且不能写下面两行ImageToTensor
    #如果三行都写会报错'DataContainer' object has no attribute 'shape'
    #如果只写两行ImageToTensor，会报错expected scalar type Long but found Byte
    # dict(type='ImageToTensor', keys=['img']),#######
    # dict(type='ImageToTensor', keys=['gt_semantic_seg']),#############
    dict(type='Collect', keys=['img', 'gt_semantic_seg'])#############
]
test_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(
        type='MultiScaleFlipAug',
        img_scale=(1000, 750),
        flip=False,
        transforms=[
            dict(type='Resize', keep_ratio=True),
            dict(type='RandomFlip'),
            dict(type='Normalize', **img_norm_cfg),
            dict(type='ImageToTensor', keys=['img']),
            dict(type='Collect', keys=['img']),
        ])
    # dict(type='RandomFlip', prob=0),#必须有RandomFlip，一般测试要设置为0
    # # dict(type='Resize', img_scale=(512, 512)),
    # # dict(type='CenterCrop', crop_size=512),
    # dict(type='Normalize', **img_norm_cfg),
    # dict(type='ImageToTensor', keys=['img']),############这个写不写都报错imgs must be a list, but got <class 'torch.Tensor'>
    # #\mmsegmentation\mmseg\models\segmentors\base.py", line 74, in forward_test
    #似乎test的type只能为MultiScaleFlipAug类型，否则就会报这个错，但是改为MultiScaleFlipAug以后就正常了
    # dict(type='Collect', keys=['img'])###############
]

dataset_type = 'CustomDataset'
classes = ['W','H','C','V','M','B','D']  # The category names of your dataset  ['W','L','H','C','V','M','A','B','D']

data = dict(
    samples_per_gpu=6, 
    workers_per_gpu=1,
    train=dict(
        type=dataset_type,
        img_dir='/home/yefan/project/mmsegmentation/data/plant_global_mask_withS/img_dir/train',
        ann_dir='/home/yefan/project/mmsegmentation/data/plant_global_mask_withS/ann_dir/train',
        classes=classes,
        palette = [[128, 64, 128], [70, 70, 70], [102, 102, 156],[190, 153, 153], [153, 153, 153], [220, 220, 0], [0,255,255]],
        # palette = [[128, 64, 128], [244, 35, 232], [70, 70, 70], [102, 102, 156],[190, 153, 153], [153, 153, 153], [250, 170, 30], [220, 220, 0], [0,255,255]],
        pipeline=train_pipeline
    ),
    val=dict(
        type=dataset_type,
        img_dir='/home/yefan/project/mmsegmentation/data/plant_global_mask_withS/img_dir/val',
        ann_dir='/home/yefan/project/mmsegmentation/data/plant_global_mask_withS/ann_dir/val',
        classes=classes,
        palette = [[128, 64, 128], [70, 70, 70], [102, 102, 156],[190, 153, 153], [153, 153, 153], [220, 220, 0], [0,255,255]],
        pipeline=test_pipeline
    ),
    test=dict(
        type=dataset_type,
        img_dir='/home/yefan/project/mmsegmentation/data/plant_global_mask_withS/img_dir/test',
        ann_dir='/home/yefan/project/mmsegmentation/data/plant_global_mask_withS/ann_dir/test',
        classes=classes,
        palette = [[128, 64, 128], [70, 70, 70], [102, 102, 156],[190, 153, 153], [153, 153, 153], [220, 220, 0], [0,255,255]],
        pipeline=test_pipeline
    )
)
# evaluation = dict(interval=1, metric='mIoU') 
evaluation = dict(interval=1, metric=['mIoU', 'mDice', 'mFscore'], pre_eval=True, save_best='mIoU')#自动保存mIOU最好的模型

# Training schedule config
# lr is set for a batch size of 128
optimizer = dict(type='SGD', lr=0.005, momentum=0.9, weight_decay=0.0001)
optimizer_config = dict(grad_clip=None)
# learning policy
lr_config = dict(policy='step', step=[15])
runner = dict(type='EpochBasedRunner', max_epochs=400)
# log_config = dict(interval=1)
log_config = dict(
    interval=1,
    hooks=[
        dict(type='TextLoggerHook'),
        dict(type='TensorboardLoggerHook')
    ])
checkpoint_config = dict(interval=5, create_symlink=False) # 每隔多少epoch保存一次模型文件