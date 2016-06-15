import os
import argparse
import numpy as np
from sklearn.preprocessing import normalize
import logging
import IPython

TO_FEATURIZE = {
    "planarity": True,
    "in_out_cone": False,
    "approx_normals": False,
    "crop_windows":False
}

def get_patch_files_and_nums(input_path, prefixes):
    file_num_pairs = []
    
    for filename in os.listdir(input_path):
        contains_prefix = [filename.startswith(prefix) for prefix in prefixes]
        
        if True in contains_prefix:
            _, ext = os.path.splitext(filename)
            num = filename[len(prefix):-len(ext)]
            
            file_num_pairs.append((filename, num))
        
    return file_num_pairs
            
def featurize_approx_normals(args):
    def get_approx_normal(img):
        l = int(np.sqrt(img.shape[0]))
        c = l // 2
        res = 0.05/15
        grad = np.gradient(img.reshape(l,l))
        normal = normalize(np.array([grad[0][c, c]/res, grad[1][c, c]/res, -1]).reshape(1,-1))
        return normal
    
    ws = ("w1", "w2")
    prefixes = [w + '_projection_window_' for w in ws]
    for filename, num in get_patch_files_and_nums(args.input_path, prefixes):
        logging.info("Approx Normals Processing " + filename)
        
        data = np.load(os.path.join(args.input_path, filename))['arr_0']
        
        normals = []
        for img in data:
            normals.append(get_approx_normal(img))
            
        normals = np.array(normals)
        wi = filename[:2]
        output_filename = wi + '_approx_normals_' + num
        logging.info("Saving " + output_filename)
        np.savez(os.path.join(args.output_path, output_filename), normals)

def featurize_planarities(args):
    ws = ("w1", "w2")
    prefixes = [w + '_projection_window_' for w in ws]
    for filename, num in get_patch_files_and_nums(args.input_path, prefixes):
        logging.info("Planarities Processing " + filename)
        
        data = np.load(os.path.join(args.input_path, filename))['arr_0']
        
        dim = int(np.sqrt(data.shape[1]))
        x_ind, y_ind = np.meshgrid(np.arange(dim), np.arange(dim))
        A = np.c_[np.ravel(x_ind), np.ravel(y_ind), np.ones(dim**2)]
        b = data.T

        w, _, _, _ = np.linalg.lstsq(A, b)
        pred_w = A.dot(w)

        pred_w_error = pred_w - b
        mean_sq_dev_planarity_w = np.mean(pred_w_error**2, axis=0)
        
        wi = filename[:2]
        output_filename = wi + '_sq_planarities_' + num
        logging.info("Saving " + output_filename)
        np.savez(os.path.join(args.output_path, output_filename), mean_sq_dev_planarity_w)

def featurize_in_out_cones(args):
    return

def featurize_crop_windows(args):
    return
    
FEATURIZER_MAP = {
    "planarity" : featurize_planarities,
    "in_out_cone" : featurize_in_out_cones,
    "crop_windows" : featurize_crop_windows,
    "approx_normals": featurize_approx_normals
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_path')
    parser.add_argument('output_path')
    args = parser.parse_args()
    
    logging.getLogger().setLevel(logging.INFO)
    
    for feature_name, to_featurize in TO_FEATURIZE.items():
        if to_featurize:
            FEATURIZER_MAP[feature_name](args)