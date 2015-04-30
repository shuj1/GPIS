function [R_grasp_obj_list, t_grasp_obj_list, g1_obj, g2_obj] = ...
    grasp_points_to_poses(grasp, sdf_centroid, sdf_res, config)
%GRASP_POINTS_TO_POSES 

% get grasp params
g1 = grasp.g1_open;
g2 = grasp.g2_open;
theta_res = config.theta_res;
pr2_grasp_offset = config.grasp_offset;

R_grasp_center = eye(1);
t_grasp_center = pr2_grasp_offset;

% centroid in volume frame of ref
centroid_m_vol = grid_to_m(sdf_centroid', sdf_res);

% get tf from vol to obj 
% R_vol_obj = ...
%     [-1, 0, 0;
%       0, 0, -1;
%       0, -1, 0]; % check jeff's diagrams (for rviz ONLY)
R_vol_obj = ...
    [1, 0, 0;
     0, 1, 0;
     0, 0, 1];
t_vol_obj = -centroid_m_vol;

% convert grasp to obj frame in meters
g1_vol = grid_to_m(g1', sdf_res);
g2_vol = grid_to_m(g2', sdf_res);

% center, then rotate
g1_obj = R_vol_obj * (g1_vol + t_vol_obj);
g2_obj = R_vol_obj * (g2_vol + t_vol_obj);
t_center_obj = (g1_obj + g2_obj) / 2;

% get rotational axes of grasp
g_y_axis = g1_obj - g2_obj;
g_y_axis = g_y_axis / norm(g_y_axis);
g_x_ref = [g_y_axis(2) -g_y_axis(1), 0]'; % dir orth to y axis
g_x_ref = g_x_ref / norm(g_x_ref);
g_z_ref = cross(g_x_ref, g_y_axis);
R_center_obj = [g_x_ref, g_y_axis, g_z_ref];
%R_grasp_obj = R_obj_grasp;

% dicretize tangent rotational direction 
theta_vals = 0:theta_res:(2*pi - theta_res);
num_theta = size(theta_vals, 2);
R_grasp_obj_list = cell(1, num_theta);
t_grasp_obj_list = cell(1, num_theta);

% find the rotation for every possible pose
for k = 1:num_theta
    theta = theta_vals(k);
    R_obj_rot_obj = ...
        [cos(theta), 0, sin(theta);
                  0, 1,          0;
        -sin(theta), 0, cos(theta)];
    R_center_obj_rot = R_obj_rot_obj * R_center_obj;
    R_grasp_obj = R_grasp_center * R_center_obj_rot;
    
    R_grasp_obj_list{k} = R_grasp_obj;
    t_grasp_obj_list{k} = t_center_obj +  R_center_obj_rot' * t_grasp_center;
end

end
