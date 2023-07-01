from mmseg.apis import inference_segmentor, init_segmentor, show_result_pyplot
import yaml
import numpy as np

yaml_path = './config.yaml'

def network_init():
    with open(yaml_path, 'r') as f:
        cfg = yaml.load(f.read(), Loader = yaml.FullLoader)
        config = cfg['network']['config_path']
        checkpoint = cfg['network']['checkpoint_path']
        device = cfg['network']['device']
        palette = cfg['network']['palette']

    model = init_segmentor(config, checkpoint, device=device)

    return model,palette



def plant_img_seg(model, img, num, palette, patch_index):

    output_path = f'./plant_imgs_seg/{patch_index}/{num}.jpg'

    # test a single image
    result = inference_segmentor(model, img) # type(result) == list
    # print(result) # len(result)==1,result[0]==array

    # np.save(f'./plant_imgs_seg/{map_patch_index}/{num}.npy',result[0])
    class0 = np.count_nonzero(result[0] == 0)
    class1 = np.count_nonzero(result[0] == 1)
    class2 = np.count_nonzero(result[0] == 2)
    class3 = np.count_nonzero(result[0] == 3)
    class4 = np.count_nonzero(result[0] == 4)
    class5 = np.count_nonzero(result[0] == 5)
    class6 = np.count_nonzero(result[0] == 6)
    class_pixel_number = [class0,class1,class2,class3,class4,class5,class6]
    # print(class_pixel_number)
    with open(f'./plant_imgs_seg/{patch_index}/{num}.txt','w') as f:
        f.write(str(class_pixel_number))

    # show the results
    show_result_pyplot(
        model,
        img,
        result,
        palette,
        opacity=1, # 透明度,0-1，1代表不显示原图
        out_file=output_path)

if __name__ == "__main__":
    
    lon_delta = 0.008050000000039859/16
    lat_delta = 0.006820000000018922/16
    lon = 118.79616307726836
    lat = 32.071561594852994
    # for i in range(1,17):
    #     for j in range(1,17):
    #         lon1 = lon+j*lon_delta
    #         lat1 = lat+i*lat_delta
    #         print(get_map_patch_index(str(lon1)+','+str(lat1)))
    img = './plant_imgs/85.jpg'
    model,palette = network_init()
    plant_img_seg(model,img,30,palette,'118.8042030772684,32.07837159485301')
        
    