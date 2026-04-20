import pathlib

p = pathlib.Path(r'L:/Documents/Perso/GPECTview/node_modules/@stlite/desktop/bin/dump_artifacts.js')
c = p.read_text(encoding='utf8')
c = c.replace(
    'zd.default.join(this.sourceUrl,e)',
    '(this.sourceUrl.endsWith("/")?this.sourceUrl+e:this.sourceUrl+"/"+e)'
)
c = c.replace(
    'ce.default.join(this.sourceUrl,e)',
    '(this.sourceUrl.endsWith("/")?this.sourceUrl+e:this.sourceUrl+"/"+e)'
)
c = c.replace(
    'ce.default.join(i,e)',
    '(i.endsWith("/")?i+e:i+"/"+e)'
)

p.write_text(c, encoding='utf8')
print("Patched.")
