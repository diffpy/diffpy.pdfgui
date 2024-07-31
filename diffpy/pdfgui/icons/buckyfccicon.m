function stru = c60fccstru(varargin)
% BUCKYFCCICON  generate PDFFIT style stru file of C60 fcc lattice
% STRU = BUCKYFCCICON    returns a string
% BUCKYFCCICON  accepts optional parameter-value pairs, which may be:
%   'a'    [10*sqrt(2)] lattice parameter of fcc cube in A
%   'd'    [7.1] diameter of Bucky ball in A
%   'r'    [] experimental coordinates of Bucky ball
%   'rot'  [1] if true, apply random rotation

% default parameters
p = struct( 'a', 10*sqrt(2),  'd', 7.1,  'r', [],  ...
            'U', 0.002,  'rot', 1 );

% process arguments
if rem(nargin, 2)
    error('number of arguments must be even')
end
for i = 1:2:nargin
    n = varargin{i};
    v = varargin{i+1};
    if ~isfield(p, n)
	error(sprintf('unknown parameter %s', n))
    end
    p = setfield(p, n, v);
end

% FCC fractional coordinates
xyzfcc = [ 0,0,0; 1,0,0; 1,1,0; 0,1,0;
           0,0,1; 1,0,1; 1,1,1; 0,1,1;
           .5,.5,.0; .5,.0,.5; .0,.5,.5;
           1.,.5,.5; .5,1.,.5; .5,.5,1. ];

Nfcc = size(xyzfcc,1);

xyzsc = xyzfcc;
Nsc = size(xyzsc,1);

if p.rot
    % generate random rotation axis and angles
    phi=2*pi*rand(Nsc,1); th=acos(2*rand(Nsc,1)-1); alph=2*pi*rand(Nsc,1);
    Rua = [sin(th).*cos(phi), sin(th).*sin(phi), cos(th), alph];
else
    % no rotation
    Rua = [ 0, 0, 1, 0 ];
    Rua = Rua(ones(Nsc,1),:);
end

% unit bucky ball
if ~isempty(p.r)
    rC60 = p.r;
    rcms = mean(rC60);
    rC60 = rC60 - rcms(ones(size(rC60,1),1),:);
    p.d = max(distmx(rC60,'s'));
else
    [ignore, uC60] = bucky();
    rC60 = uC60 * p.d/2.0;
end
rall = [];
for i = 1:Nsc
    rall = [rall;
	xyzsc(i*ones(size(rC60,1),1),:)*p.a + rotateua(Rua(i,:), rC60)
    ];
end
Nall = size(rall,1);

abc = diag([1,1,1] * p.a);
% finally build the PDFFIT stru string
stru = {
    sprintf('title  fcc C60, d=%g, a=%g\n', p.d, p.a)
    sprintf('format pdffit\n')
    sprintf('scale   1.000000\n')
    sprintf('sharp   0.000000,  1.000000,  0.000000\n')
    sprintf('spcgr  P1\n')
    sprintf('cell  %10.6f,%10.6f,%10.6f,%10.6f,%10.6f,%10.6f\n', ...
	diag(abc), 90, 90, 90)
    sprintf('dcell %10.6f,%10.6f,%10.6f,%10.6f,%10.6f,%10.6f\n', ...
	zeros(1,6))
    sprintf('ncell %8i,%8i,%8i,%8i\n', 1, 1, 1, Nall)
    sprintf('atoms\n')
};
for i = 1:Nall
    stru{end+1} = sprintf( '%-4s%18.8f%18.8f%18.8f%13.4f\n', ...
	'C', rall(i,:)/abc, 1.0,    '', zeros(1,3), 0.0 );
    stru{end+1} = sprintf( '%22.8f%18.8f%18.8f\n', ...
	p.U(ones(1,3)),  zeros(3,3) );
end

stru = [ stru{:} ];

function r1 = rotateua(ua, r0)
% hacked from ROTATE
x = ua(1);
y = ua(2);
z = ua(3);
alph = ua(4);
cosa = cos(alph);
sina = sin(alph);
vera = 1 - cosa;
rot = [cosa+x^2*vera x*y*vera-z*sina x*z*vera+y*sina; ...
       x*y*vera+z*sina cosa+y^2*vera y*z*vera-x*sina; ...
       x*z*vera-y*sina y*z*vera+x*sina cosa+z^2*vera]';
r1 = r0*rot;
