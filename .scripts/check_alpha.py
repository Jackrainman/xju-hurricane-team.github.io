from PIL import Image
from collections import Counter
p = r'd:\\Documents\\xju-hurricane-team.github.io\\docs\\img\\logo.png'
im = Image.open(p)
print('mode:', im.mode)
print('size:', im.size)
print('bands:', im.getbands())
has_alpha = 'A' in im.getbands()
print('has_alpha:', has_alpha)
if has_alpha:
    alpha = im.split()[-1]
    cnt = Counter(alpha.getdata())
    print('alpha unique values count:', len(cnt))
    print('alpha sample (up to 10):', list(cnt.items())[:10])
else:
    print('No alpha channel')
