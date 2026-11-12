import io, os, re, sys, zipfile

FOX, DEV = sys.argv[1:3]
T = os.path.join(FOX, 'bootable/recovery/gui/theme/portrait_hdpi')
F = os.path.join(FOX, 'bootable/recovery/gui/theme/common/fonts')
UI = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui')
ROOT = os.path.join(DEV, 'recovery/root')

def path(n):
    assert n.startswith('twres/'), n
    r = n[len('twres/'):]
    return os.path.join(F, r[len('fonts/'):]) if r.startswith('fonts/') else os.path.join(T, r)

def find_changelog():
    for base in ('bootable/recovery', 'vendor/recovery'):
        for dp, _, fns in os.walk(os.path.join(FOX, base)):
            if 'changelog.txt' in fns and '.git' not in dp:
                c = os.path.join(dp, 'changelog.txt')
                if b'OrangeFox' in open(c, 'rb').read(200):
                    return c
    return None

class Res(dict):
    def __missing__(self, n):
        p = find_changelog() if n == 'twres/changelog.txt' else path(n)
        if p is None or not os.path.exists(p):
            raise KeyError(n)
        self[n] = [p, open(p, 'rb').read()]
        return self[n]

res = Res()
new = {}

def asset(n):
    return open(os.path.join(UI, n), 'rb').read()

def sub(text, old, new_, count=1):
    assert text.count(old) == count, old[:80]
    return text.replace(old, new_)

def page(text, name):
    p0 = text.index('<page name="%s">' % name)
    return p0, text.index('</page>', p0)

def mkzip(binary):
    b = io.BytesIO()
    with zipfile.ZipFile(b, 'w', zipfile.ZIP_DEFLATED) as z:
        for n, d, m in (('META-INF/com/google/android/update-binary', binary, 0o755),
                        ('META-INF/com/google/android/updater-script', b'#MENG\n', 0o644)):
            i = zipfile.ZipInfo(n, (2026, 1, 1, 0, 0, 0))
            i.external_attr = (0o100000 | m) << 16
            i.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(i, d)
    return b.getvalue()

def text(n):
    return res[n][1].decode()

def put(n, s):
    res[n][1] = s.encode() if isinstance(s, str) else s

new[path('twres/images/Default/About/maintainer.png')] = asset('maintainer.png')
new[path('twres/fonts/MengName.ttf')] = asset('MengName.ttf')
ix = text('twres/resources/images.xml')
ix = sub(ix, '<resources>', '<resources>\n\t\t<font name="meng_name" filename="MengName.ttf" size="56"/>')
put('twres/resources/images.xml', ix)

st = text('twres/pages/settings.xml')
mre = re.compile(r'<text style="about_name">(\s*(?:<condition[^>]*/>\s*){3}<placement x="%card_txt_x%" y="%card_img4_y%"/>\s*)<text>%of_maintainer%</text>')
assert len(mre.findall(st)) == 1, 'about_name'
st = mre.sub(lambda m: '<text>\n\t\t\t\t<font resource="meng_name" color="%text%"/>' + m.group(1) + '<text>ᴶᵁᴻᴵ༄</text>', st)
st = sub(st, '<text>{@version}: %fox_actual_build%</text>', '<text>{@version}: R12.1</text>')
put('twres/pages/settings.xml', st)

try:
    put('twres/changelog.txt', asset('changelog_c330.txt') + b'\n' + res['twres/changelog.txt'][1])
except KeyError:
    print('W: changelog.txt not found, skipped')

ax = text('twres/pages/advanced.xml')
a0, a1 = page(ax, 'advanced')
ap = ax[a0:a1]
ICONS = ('addons', 'android', 'apps_box', 'devices', 'kernelsu', 'mount_list', 'other', 'overview',
         'partitions', 'restart', 'wand_shine', 'wrench')
PM = '''				<listitem name="{@partitions_management}">
					<icon res="partitions"/>
					<action function="page">part_manage</action>
				</listitem>
'''
ap = sub(ap, PM, '')
for o, n in (('<listbox style="group_list">\n\t\t\t\t<placement x="0" y="%row1_1a_y%" w="%screen_w%" h="%files_np_w%"/>',
              '<listbox style="group_list_c330">\n\t\t\t\t<placement x="0" y="%row1_1a_y%" w="%screen_w%" h="360"/>'),
             ('<placement x="%gl_text_x%" y="%row4_3_y%"/>', '<placement x="%gl_text_x%" y="720+%cutout_w%"/>'),
             ('<listbox style="group_list">\n\t\t\t\t<placement x="0" y="%row5_1_y%" w="%screen_w%" h="%adv_additions_h%"/>',
              '<listbox style="group_list_c330">\n\t\t\t\t<placement x="0" y="780+%cutout_w%" w="%screen_w%" h="720"/>')):
    ap = sub(ap, o, n)
for ic in ICONS:
    ap = ap.replace('<icon res="%s"/>' % ic, '<icon res="%s_c330"/>' % ic)
r0 = ap.index('<listitem name="{@reflash_twrp}">'); r1 = ap.index('</listitem>', r0) + len('</listitem>')
ap = ap[:r0] + """<listitem name="Disable stock recovery">
					<icon res="wrench_c330"/>
					<action function="queueclear"/>
					<action function="set">fox_m_author=Meng</action>
					<action function="set">fox_m_name=Disable stock recovery</action>
					<action function="set">tw_file=meng_nostock.zip</action>
					<action function="set">tw_filename=/FFiles/MengNoStock/meng_nostock.zip</action>
					<action function="set">tw_filecheck=%tw_filename%</action>
					<action function="set">tw_zip_location=/FFiles/MengNoStock</action>
					<action function="set">fox_install_built_in_zip=1</action>
					<action function="queuezip"/>
					<action function="set">install_back=advanced</action>
					<action function="set">tw_notexistpage=fox_modules_confirm</action>
					<action function="set">tw_existpage=fox_modules_confirm</action>
					<action function="page">filecheck</action>
				</listitem>""" + ap[r1:]
ax = ax[:a0] + ap + ax[a1:]

tfs = [os.path.join(T, 'themes', fn) for fn in os.listdir(os.path.join(T, 'themes')) if fn.endswith('.xml')]
sd = os.path.join(T, 'themes', 'styles')
if os.path.isdir(sd):
    tfs += [os.path.join(sd, fn) for fn in os.listdir(sd) if fn.endswith('.xml')]
nicons = 0
for tf in tfs:
    tx = open(tf, encoding='utf-8').read()
    hit = False
    for ic in ICONS:
        m = re.search(r'^([ \t]*)<image name="%s" ([^\n]*?)scale="([0-9.]+)"([^\n]*)$' % ic, tx, re.M)
        if not m:
            continue
        hit = True
        sc = '%.2f' % (float(m.group(3)) * 0.85)
        line = '%s<image name="%s_c330" %sscale="%s"%s' % (m.group(1), ic, m.group(2), sc, m.group(4))
        tx = tx[:m.end()] + '\n' + line + tx[m.end():]
        nicons += 1
    if hit:
        new[tf] = tx.encode('utf-8')
assert nicons >= len(ICONS), nicons

sx = text('twres/resources/styles.xml')
g0 = sx.index('<style name="group_list">'); g1 = sx.index('</style>', g0) + len('</style>')
gs = sx[g0:g1]
for o, n in (('name="group_list"', 'name="group_list_c330"'),
             ('<iconsize w="216" h="%bl_h1%" padding="24"/>', '<iconsize w="216" h="120" padding="24"/>'),
             ('<font resource="button"', '<font resource="font_s"')):
    gs = sub(gs, o, n)
sx = sx[:g1] + '\n\n\t\t' + gs + sx[g1:]
put('twres/resources/styles.xml', sx)

o0, o1 = page(ax, 'fox_other_additions')
op = ax[o0:o1]
lb = '<placement x="0" y="%ab_h%" w="%screen_w%" h="%files_np_w%"/>\n'
op = sub(op, lb, lb + PM)
ax = ax[:o0] + op + ax[o1:]
m0, m1 = page(ax, 'part_manage')
mp = ax[m0:m1]
mp = sub(mp, '<touch key="back"/>\n\t\t\t\t<action function="page">advanced</action>',
         '<touch key="back"/>\n\t\t\t\t<action function="page">fox_other_additions</action>')
ax = ax[:m0] + mp + ax[m1:]
p0, p1 = page(ax, 'fox_modules')
pg = ax[p0:p1]
pg = sub(pg, '<action function="set">install_back=fox_modules</action>\n',
         '<action function="set">install_back=fox_modules</action>\n\t\t\t\t<action function="set">meng_reboot_rec=0</action>\n\t\t\t\t<action function="set">meng_dfe_neo=0</action>\n')
ksu_c = '<condition var1="fox_support_ksu" var2="1"/>'
if ax.count(ksu_c):
    pg = pg.replace(ksu_c, ksu_c + '\n                <condition var1="fileexists" var2="/FFiles/KernelSU"/>')
pg = sub(pg, '<placement x="0" y="%row3_2a_y%" w="%screen_w%" h="%bl_h4%"/>',
         '<placement x="0" y="%row3_2a_y%" w="%screen_w%" h="720"/>')
ax = ax[:p0] + pg + ax[p1:]

Z, ZD = 'meng_dfe.zip', '/FFiles/MengDFE'
ZP = ZD + '/' + Z
item = '''				<listitem name="Disable encryption (DFE)">
					<condition var1="fileexists" var2="%(zp)s"/>
					<icon res="archive"/>
					<action function="queueclear"/>
					<action function="set">fox_m_author=Meng</action>
					<action function="set">fox_m_name=Disable encryption (DFE)</action>
					<action function="set">tw_file=%(z)s</action>
					<action function="set">tw_filename=%(zp)s</action>
					<action function="set">tw_filecheck=%%tw_filename%%</action>
					<action function="set">tw_zip_location=%(zd)s</action>
					<action function="set">fox_install_built_in_zip=1</action>
					<action function="queuezip"/>
					<action function="set">tw_notexistpage=fox_modules_confirm</action>
					<action function="set">tw_existpage=fox_modules_confirm</action>
					<action function="page">filecheck</action>
				</listitem>
''' % dict(z=Z, zp=ZP, zd=ZD)
anchor = '				<listitem name="{@module_of_set}">'
ax = sub(ax, anchor, item + anchor)
put('twres/pages/advanced.xml', ax)

ix2 = text('twres/pages/install.xml')
f0, f1 = page(ix2, 'flash_confirm')
fcp = ix2[f0:f1]
rb_item = '''				<listitem name="{@install_reboot_chk}">'''
fcp = sub(fcp, rb_item, '''				<listitem name="Reboot to recovery after install">
					<data variable="meng_reboot_rec"/>
				</listitem>
				<listitem name="Auto DFE after install">
					<condition var1="fileexists" var2="%s"/>
					<data variable="meng_dfe_neo"/>
				</listitem>
''' % ZP + rb_item)
for key in ('back', 'home'):
    t = '\t\t\t\t<touch key="%s"/>\n\t\t\t\t<action function="queueclear"/>\n' % key
    fcp = sub(fcp, t, t + '\t\t\t\t<action function="set">meng_reboot_rec=0</action>\n\t\t\t\t<action function="set">meng_dfe_neo=0</action>\n')
fl = '\t\t\t\t<action function="flash">flash_zip</action>\n'
fcp = sub(fcp, fl, fl + '\t\t\t\t<action function="cmd">/system/bin/meng_postflash.sh %meng_reboot_rec% %meng_dfe_neo% %tw_install_reboot% %tw_operation_status%</action>\n')
ix2 = ix2[:f0] + fcp + ix2[f1:]

d0, d1 = page(ix2, 'flash_done')
fd = ix2[d0:d1]
old_rb = '''				<condition var1="tw_install_reboot" var2="1"/>
				<condition var1="tw_operation_status" var2="0"/>
				<condition var1="tw_reboot_system" var2="1"/>
'''
fd = sub(fd, old_rb, old_rb + '\t\t\t\t<condition var1="meng_reboot_rec" op="!=" var2="1"/>\n\t\t\t\t<condition var1="meng_dfe_neo" op="!=" var2="1"/>\n\t\t\t\t<condition var1="meng_job" op="!=" var2="1"/>\n')
note = '''			<text style="text_body1">
				<condition var1="tw_operation_status" var2="0"/>
				<condition var1="meng_reboot_rec" var2="1"/>
				<placement x="%gl_text_x%" y="%row_btn1_y%-90"/>
				<text>Auto: rebooting to recovery...</text>
			</text>

			<text style="text_body1">
				<condition var1="tw_operation_status" var2="0"/>
				<condition var1="meng_reboot_rec" op="!=" var2="1"/>
				<condition var1="meng_dfe_neo" var2="1"/>
				<placement x="%gl_text_x%" y="%row_btn1_y%-90"/>
				<text>Auto: rebooting to recovery for DFE...</text>
			</text>

'''
fd = sub(fd, '\t\t\t<action>\n' + old_rb, note + '\t\t\t<action>\n' + old_rb)
for t in ('\t\t\t\t<touch key="back"/>\n', '\t\t\t\t<touch key="home"/>\n'):
    fd = sub(fd, t, t + '\t\t\t\t<action function="set">meng_job=0</action>\n')
ix2 = ix2[:d0] + fd + ix2[d1:]

J = '/persist/OFRP/meng_job'
pre = '\t\t\t\t<action function="cmd">/system/bin/meng_dfe_job.sh pre</action>\n'
fz = '\t\t\t\t<action function="flash">flash_zip</action>\n'
post = '\t\t\t\t<action function="cmd">/system/bin/meng_dfe_job.sh post %tw_operation_status%</action>\n'
job = '''		<page name="meng_auto_job">
			<template name="base_ex"/>

			<action>
				<action function="set">meng_job=1</action>
				<action function="set">install_back=filemanagerlist</action>
				<action function="queueclear"/>
			</action>

			<action>
				<condition var1="fileexists" var2="%(J)s/dfe"/>
				<action function="set">tw_file=%(z)s</action>
				<action function="set">tw_filename=%(zp)s</action>
				<action function="set">tw_zip_location=%(zd)s</action>
				<action function="set">fox_install_built_in_zip=1</action>
				<action function="queuezip"/>
			</action>

			<action>
				<condition var1="fileexists" var2="%(J)s/zip"/>
%(pre)s%(fz)s%(post)s			</action>

			<action>
				<condition var1="fileexists" op="!=" var2="%(J)s/zip"/>
%(pre)s				<action function="cmd">/system/bin/meng_dfe_job.sh final</action>
				<action function="set">meng_job=0</action>
				<action function="page">filemanagerlist</action>
			</action>
		</page>

''' % dict(J=J, z=Z, zp=ZP, zd=ZD, pre=pre, fz=fz, post=post)
k = ix2.index('</page>', ix2.index('<page name="flash_confirm">')) + len('</page>\n')
ix2 = ix2[:k] + '\n' + job + ix2[k:]
put('twres/pages/install.xml', ix2)

mx = text('twres/pages/main.xml')
n0, n1 = page(mx, 'navbar')
mx = mx[:n1] + '''	<action>
				<condition var1="fileexists" var2="%s/go"/>
				<action function="page">meng_auto_job</action>
			</action>
		''' % J + mx[n1:]
put('twres/pages/main.xml', mx)

vx = text('twres/resources/vars.xml')
vx = sub(vx, '<variables>', '<variables>\n\t\t<variable name="meng_reboot_rec" value="0"/>\n\t\t<variable name="meng_dfe_neo" value="0"/>\n\t\t<variable name="meng_job" value="0"/>')
put('twres/resources/vars.xml', vx)

sp = text('twres/splash.xml')
lo = '<image resource="splash_logo"/>\n\t\t\t\t<placement x="540" y="%center_y%" placement="4"/>'
sp = sub(sp, lo, lo.replace('y="%center_y%"', 'y="840"'))
put('twres/splash.xml', sp)

new[os.path.join(ROOT, 'FFiles/MengNoStock/meng_nostock.zip')] = mkzip(asset('nostock-update-binary'))
new[os.path.join(ROOT, 'FFiles/MengDFE/meng_dfe.zip')] = mkzip(asset('mengdfe-update-binary'))

for n, (p, d) in res.items():
    new[p] = d
for p, d in new.items():
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'wb').write(d)
    print('wrote', os.path.relpath(p, FOX) if p.startswith(FOX) else p)
