//+
SetFactory("OpenCASCADE");
Box(1) = {0, 0, 0, 1, 1, 1};
//+
Physical Surface("cube_tope", 13) = {2};
//+
Physical Surface("cube_top", 14) = {2};
//+
Physical Surface("cube_bottom", 15) = {1};
//+
Physical Surface("cube_left", 16) = {3};
//+
Physical Surface("cube_front", 17) = {4, 5};
//+
Physical Surface(" cube_tope", 13) -= {2};
//+
Physical Surface(" cube_front", 17) -= {4, 5};
//+
Physical Surface("cube_right", 18) = {4};
//+
Physical Surface("cube_front", 19) = {5};
//+
Physical Surface("cube_back", 20) = {6};
