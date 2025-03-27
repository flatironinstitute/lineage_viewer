

% convert from mat lineage to json lineage for visualization

lineage_file = '/Users/lbrown/Documents/projects/Visualizations/segmentation_viz_workflow/examples-Aaron/BS1_graph.mat'


gg = load(lineage_file);

gg = gg.G_based_on_nn;


figure;
H = plot(gg)
layout(H,'layered'); %,'Sources',[15 13 11]);


% output for python reading
jH = jsonencode(gg);

%fid = fopen(strcat(data_path, '/GT_tracking_F32_to_F40.json'),'w');

fid = fopen(strcat(lineage_file(1:size(lineage_file,2)-4),'.json'),'w');
fprintf(fid, jH)

fclose(fid)
