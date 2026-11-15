function D = dummies(r)
% one column per category of r, dropping the first category present
c = unique(r);
D = double(r(:) == c(2:end)');
end
