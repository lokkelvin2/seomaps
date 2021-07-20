fig = uifigure;
fig.Position = [100 100 1842 916];

h = uihtml(fig);
h.Position = [1 1 1842 916];

h.HTMLSource = fullfile(pwd,'foliumplotvector.matlab.html');

% then load countries.geojson into canvas

