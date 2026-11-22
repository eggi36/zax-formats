#!/bin/sh
# Self-test of the pre-push hook next to this file: scratch repositories under a temporary folder, a made-up local.json
# (ZAX_LOCAL_JSON; the real one is never read), one commit or tag per case, the hook fed the push line by hand.
# Every case that holds a made-up private value, a home path, an e-mail address or game data must be refused, the clean
# ones must pass. A refusal counts only with the finding the case is about ($expect, a fixed text of the hook's message;
# review5 P55-6). The made-up home paths, addresses and key lines are split by '' so this file itself passes the hook.
# Run: sh tools/git-hooks/test-pre-push.sh   (exit 0 = all cases as expected)
hook=$(cd "$(dirname "$0")" && pwd)/pre-push
tmp=$(mktemp -d) || exit 1
trap 'rm -rf "$tmp"' EXIT
zero=0000000000000000000000000000000000000000
at=@
noreply="86563507+tester${at}users.noreply.github.com"
cat > "$tmp/local.json" <<EOF
{"share_root": "/Mnt", "share_prefix": "QSHR-", "extra_globs": ["QGLB-*"],
 "lan": {"host": "QVMH-01", "client": "QVMC-01", "client2": "QVMC-02", "host_ip": "10.79.68.57",
         "names": ["Plyrzork", "Plyrwemb"], "game_host_ip": "10.79.68.58"},
 "macvm": {"name": "QMACVM", "host": "10.79.69.5", "user": "qmacuser", "key": "~/.ssh/qmackey"},
 "private_words": ["Quxblorf", "Fnordel"], "exclude": ["QVMX-09"]}
EOF
printf '{"private_words": []}\n' > "$tmp/nowords.json"
export ZAX_LOCAL_JSON="$tmp/local.json"
unset ZAX_PREPUSH_ALL
fails=0 tag= hookenv= expect= line=

setup() {  # setup <folder name>: a repository with one clean commit, $base
    repo="$tmp/$1"
    git init -q "$repo" && cd "$repo" || exit 1
    git config user.name tester && git config user.email "$noreply" && git config core.hooksPath /dev/null
    echo clean > README.md && git add README.md && git commit -qm "Clean start" && base=$(git rev-parse HEAD)
}
run() {  # run <expected exit> <case> [<remote_sha>]: the hook on HEAD (and on $tag if set; $line replaces the push line)
    want=$1 name=$2 old=${3:-$base}
    [ -z "$line" ] && line="refs/heads/main $(git rev-parse HEAD) refs/heads/main $old"
    [ -n "$tag" ] && line="$line
refs/tags/$tag $(git rev-parse "refs/tags/$tag") refs/tags/$tag $zero"
    printf '%s\n' "$line" | env $hookenv "$hook" origin url >"$tmp/out" 2>&1
    got=$?
    [ "$got" -ne 0 ] && got=1
    grep -qE 'Traceback|git [a-z-]+ failed' "$tmp/out" && got=error   # a refusal must come from a finding
    # a refusal for another reason than the case's is no pass (review5 P55-6)
    [ "$got" = 1 ] && [ -n "$expect" ] && ! grep -qF -- "$expect" "$tmp/out" && got="1 without \"$expect\""
    if [ "$got" = "$want" ]; then echo "ok    $name"; else echo "FAIL  $name (exit $got, expected $want)"; sed 's/^/      /' "$tmp/out"; fails=$((fails + 1)); fi
    git reset -q --hard "$base"; git tag -d "$tag" >/dev/null 2>&1; tag= hookenv= expect= line=
}
commit() {  # commit <path> <content printf format> [git commit options...]
    p=$1 c=$2; shift 2
    mkdir -p "$(dirname "$p")" && printf "$c" > "$p" && git add -f "$p" && git commit -q "$@"
}
commit16() {  # commit16 <path> <UTF-16LE|UTF-16BE> <byte order mark printf format or ''> <text>: a UTF-16 text file
    p=$1 enc=$2 bom=$3 c=$4
    mkdir -p "$(dirname "$p")" && { printf "$bom"; printf '%s\n' "$c" | iconv -f UTF-8 -t "$enc"; } > "$p" &&
        git add -f "$p" && git commit -q -m ok
}

setup zax-public
commit a.txt 'fine\n' -m 'Clean change' && run 0 "clean commit"
commit a.txt 'fine\n' -m 'Fix for quxBLORF' && expect="a private word" run 1 "message: private word (other case)"
commit a.txt 'fine\n' -m 'ok' --author "Fnordel Smith <$noreply>" && expect="a private word" run 1 "author name: private word"
commit a.txt 'fine\n' -m 'ok' --author "tester <somebody${at}mail.invalid>" && expect="other than a GitHub noreply" run 1 "author e-mail: not noreply"
export GIT_COMMITTER_NAME=Quxblorf; commit a.txt 'fine\n' -m 'ok'; unset GIT_COMMITTER_NAME; expect="a private word" run 1 "committer name: private word"
commit a.txt 'fine\n' -m 'Seen on QVMH-01' && expect="a VM name" run 1 "message: VM name"
commit a.txt 'fine\n' -m 'path /Users/''someone/x' && expect="a home folder path" run 1 "message: home path"
commit 'docs/QSHR-01.txt' 'fine\n' -m ok && expect="test setup" run 1 "file name: share prefix"
commit 'docs/plyrzork.txt' 'fine\n' -m ok && expect="test setup" run 1 "file name: player name in another case (any case since RV-10)"
commit 'docs/Plyrzork.txt' 'fine\n' -m ok && expect="test setup" run 1 "file name: player name"
commit a.txt 'host 10.79.68.200\n' -m ok && expect="test setup" run 1 "content: address /24 prefix"
commit a.txt 'key ~/.ssh/qmackey\n' -m ok && expect="test setup" run 1 "content: mac VM key"
commit a.txt 'QVMX-09 is busy\n' -m ok && expect="a VM name" run 1 "content: excluded VM name"
commit a.txt 'see QGLB-7\n' -m ok && expect="test setup" run 1 "content: extra glob"
commit a.txt 'mail somebody''@''mail.invalid\n' -m ok && expect="names an e-mail address" run 1 "content: e-mail address"
commit a.txt "mail name${at}example.org or $noreply\\n" -m ok && run 0 "content: example.org and noreply addresses"
commit a.txt 'cd /home/''someone/zax\n' -m ok && expect="a home folder path" run 1 "content: /home path"
commit a.txt 'C:\\\\Users\\\\''someone\\\\Temp\n' -m ok && expect="a home folder path" run 1 "content: Windows home path (doubled backslashes)"
commit a.txt 'C:\\Users\\''someone\\Temp\n' -m ok && expect="a home folder path" run 1 "content: Windows home path"
commit a.txt 'C:\\Users\\Zaxvm\\Temp\n' -m ok && run 0 "content: allowed made-up Windows user"
commit a.txt 'cd /Users/''someone\n' -m ok && expect="a home folder path" run 1 "content: home path at the line's end (no slash after the name)"
commit a.txt '{"HOME": "/home/''someone"}\n' -m ok && expect="a home folder path" run 1 "content: home path before a quote"
commit a.txt 'set C:\\Users\\''someone\n' -m ok && expect="a home folder path" run 1 "content: Windows home path at the line's end"
commit a.txt 'cd /Users/Zaxvm\n' -m ok && run 0 "content: allowed made-up user (no slash after the name)"
commit a.txt 'a POSIX folder ("/Users/...") or /home/..\n' -m ok && run 0 "content: a name of dots only is no user"
commit a.txt 'seen on qvmh-01\n' -m ok && expect="a VM name" run 1 "content: VM name in another case"
commit a.txt 'fine\n' -m 'Seen on Qvmx-09' && expect="a VM name" run 1 "message: excluded VM name in another case"
commit16 u.txt UTF-16LE '\377\376' "mail somebody""${at}mail.invalid" && expect="names an e-mail address" run 1 "UTF-16LE text (byte order mark): e-mail address"
commit16 u.txt UTF-16LE '' "cd /Users/""someone" && expect="a home folder path" run 1 "UTF-16LE text (no byte order mark): home path, no slash after the name"
commit16 u.txt UTF-16BE '\376\377' "For Quxblorf" && expect="a private word" run 1 "UTF-16BE text (byte order mark): private word"
commit16 u.txt UTF-16BE '' "mail somebody""${at}mail.invalid" && expect="names an e-mail address" run 1 "UTF-16BE text (no byte order mark): e-mail address"
commit16 u.txt UTF-16BE '' "on qvmh-01" && expect="a VM name" run 1 "UTF-16BE text: VM name in another case"
commit16 u.txt UTF-16LE '\377\376' "mail name${at}example.org, nothing else" && run 0 "UTF-16LE text: clean (example.org)"
commit16 u.txt UTF-16BE '' "Nothing private here at all" && run 0 "UTF-16BE text: clean"
commit a.bin '\211PNG\000\000xxQUXBLORFxx\000' -m ok && expect="a private word" run 1 "binary: private word"
commit a.bin '\211PNG\000\000Q\000u\000x\000b\000l\000o\000r\000f\000' -m ok && expect="a private word" run 1 "binary: private word as UTF-16"
commit a.bin '\001\000\000/Users/''someone/\000' -m ok && expect="a home folder path" run 1 "binary: home path"
commit a.qm '\074\270\144\030\000\000\000Q\000u\000x\000b\000l\000o\000r\000f\001' -m ok && expect="a private word" run 1 "binary: private word as UTF-16BE"
commit a.qm '\074\270\144\030\001\000\000/\000h\000o\000m\000e\000/\000s\000x\001' -m ok && expect="a home folder path" run 1 "binary: home path as UTF-16BE"
commit a.qm '\074\270\144\030\001\000\000C\000:\000\\\000U\000s\000e\000r\000s\000\\\000s\001' -m ok && expect="a home folder path" run 1 "binary: Windows home path as UTF-16BE"
commit a.bin '\001\002\000\000plain\000' -m ok && run 0 "binary: clean"
commit sub/x.RED 'fine\n' -m ok && expect="looks like game data" run 1 "game data: .RED anywhere"
commit sub/model.mdl16 'fine\n' -m ok && expect="looks like game data" run 1 "game data: .mdl16"
commit tools/ZAX.EXE 'fine\n' -m ok && expect="looks like game data" run 1 "game data: Zax.exe"
commit sub/blob.bin 'PK\003\004\024\000\000\000' -m ok && expect="is a zip, exe" run 1 "game data: zip content"
commit sub/blob.bin 'MZ\220\000\003\000' -m ok && expect="is a zip, exe" run 1 "game data: exe content"
commit gamedata/readme.txt 'fine\n' -m ok && expect="contains gamedata/" run 1 "game data: gamedata/"
commit a.txt 'see qshr-01\n' -m ok && expect="test setup" run 1 "content: share prefix in another case (review4 C7)"
commit a.txt 'on QMACVM\n' -m ok && expect="a VM name" run 1 "content: mac VM name"
commit a.txt 'user qmacuser\n' -m ok && expect="test setup" run 1 "content: mac VM user"
commit a.txt 'ssh 10.79.69.5\n' -m ok && expect="test setup" run 1 "content: mac VM host"
commit a.txt 'QVMC-02 joins\n' -m ok && expect="a VM name" run 1 "content: second LAN client"
commit a.txt 'Plyrwemb won\n' -m ok && expect="test setup" run 1 "content: second player name"
commit a.txt 'game at 10.79.68.58\n' -m ok && expect="test setup" run 1 "content: game host address"
commit sub/x.wav 'fine\n' -m ok && expect="looks like game data" run 1 "game data: .wav name"
commit sub/x.OGG 'fine\n' -m ok && expect="looks like game data" run 1 "game data: .ogg name"
commit sub/x.bik 'fine\n' -m ok && expect="looks like game data" run 1 "game data: .bik name"
commit sub/GamePalette.pal 'fine\n' -m ok && expect="looks like game data" run 1 "game data: .pal (review4 G8)"
commit sub/x.zgt 'fine\n' -m ok && expect="looks like game data" run 1 "game data: .zgt"
commit sub/Editor.pak 'fine\n' -m ok && expect="looks like game data" run 1 "game data: .pak (review4 F5)"
commit sub/sprite.TGA 'fine\n' -m ok && expect="looks like game data" run 1 "game data: .tga"
commit cfg/Zax.CFG 'fine\n' -m ok && expect="looks like game data" run 1 "game data: Zax.CFG by name"
commit text/Local.txt 'fine\n' -m ok && expect="looks like game data" run 1 "game data: Local.txt by name"
commit a.ini '[Options]\nCD Key''=ABCD-1234\n' -m ok && expect='"CD Key=" line' run 1 "game data: a CD Key= line (review4 F5)"
commit a.txt 'the CD Key line of Zax.CFG is never printed\n' -m ok && run 0 "content: CD Key named in prose"
commit sub/blob.bin 'OggS\000\002\000' -m ok && expect="is a zip, exe" run 1 "game data: Ogg content"
commit sub/blob.bin 'RIFF\044\000\000\000WAVEfmt \000' -m ok && expect="is a zip, exe" run 1 "game data: RIFF WAVE content"
commit sub/blob.bin 'BIKi\000\000\000' -m ok && expect="is a zip, exe" run 1 "game data: Bink content"
commit sub/blob.bin 'BM\066\000\000\000' -m ok && expect="BMP" run 1 "game data: BMP content"
commit docs/shot.png 'fine\n' -m ok && expect="an image outside" run 1 "image by name outside an allowed folder"
commit sub/pic.bin '\211PNG\r\n\032\n\000' -m ok && expect="an image outside" run 1 "image by content (PNG) outside an allowed folder"
commit Gamedata/x.txt 'fine\n' -m ok && expect="contains gamedata/" run 1 "game data: Gamedata/ in another case (review5 P55-6)"
commit reimpl/third_party/lib/README 'by someone''@''mail.invalid in /home/''someone\n' -m ok && run 0 "third-party folder: e-mail and home path allowed"
commit 'reimpl/third_party/Users/''someone/a.c' 'fine\n' -m ok && expect="a home folder path" run 1 "third-party folder: a home path in a file name still refused"
commit tools/gamedata/x.txt 'fine\n' -m ok && expect="contains gamedata/" run 1 "game data: a nested gamedata/ folder"
git checkout -qb side2 && commit gamedata/Rules.txt 'fine\n' -m add && git rm -q gamedata/Rules.txt && git commit -qm rm &&
    { git checkout -q main 2>/dev/null || git checkout -q master; } && git merge -q --no-ff side2 -m 'Merge side2' &&
    expect="contains gamedata/" run 1 "game data: a merged side branch that added and deleted gamedata/"; git branch -qD side2
commit sub/pic.bin 'RIFF\044\000\000\000WEBPVP8 \000' -m ok && expect="an image outside" run 1 "image by content (WebP) outside an allowed folder"
commit sub/pic.bin '\000\000\001\000\001\000\020\020\000' -m ok && expect="an image outside" run 1 "image by content (ICO) outside an allowed folder"
commit reimpl/third_party/lib/README 'by Quxblorf\n' -m ok && expect="a private word" run 1 "third-party folder: private word still refused"
commit README.zlib 'by madler''@''alumni.caltech.edu\n' -m ok && run 0 "MAIL_ALLOW address outside the third-party folders"
head -c 21000000 /dev/zero | tr '\0' 'a' > big.txt && git add big.txt && git commit -qm big && expect="larger than 20 MB" run 1 "a file over 20 MB"
git checkout -qb side && commit s.txt 'side\n' -m side && git checkout -q main 2>/dev/null || git checkout -q master
git merge -q --no-ff --no-commit side >/dev/null 2>&1; printf 'Quxblorf\n' > m.txt && git add m.txt && git commit -qm 'Merge side' &&
    expect="a private word" run 1 "merge commit: a file the merge itself adds (diff-tree -m)"; git branch -qD side
commit a.txt 'fine\n' -m ok && line="(delete) $zero refs/heads/old $base" run 0 "a branch deletion line"
commit a.txt 'fine\n' -m ok && git tag lw1 && tag=lw1 && run 0 "clean lightweight tag"
commit a.txt 'fine\n' -m 'Quxblorf' && git tag lw1 && line="refs/tags/lw1 $(git rev-parse lw1) refs/tags/lw1 $zero" expect="a private word" run 1 "lightweight tag: its commit is checked"
git tag tr1 "$(git rev-parse 'HEAD^{tree}')" && line="refs/tags/tr1 $(git rev-parse tr1) refs/tags/tr1 $zero" expect="points to a tree" run 1 "a tag that points to a tree"; git tag -d tr1 >/dev/null
git tag bl1 "$(git rev-parse HEAD:README.md)" && line="refs/tags/bl1 $(git rev-parse bl1) refs/tags/bl1 $zero" expect="points to a blob" run 1 "a tag that points to a blob"; git tag -d bl1 >/dev/null
# a push from a linked worktree: the repository's name comes from the common folder (zax-public, not the worktree's)
git worktree add -q "$tmp/wt-zax-redone" -b wtb >/dev/null 2>&1 && cd "$tmp/wt-zax-redone" &&
    commit a.txt 'QVMH-01\n' -m ok && expect="a VM name" run 1 "linked worktree of a public repository: VM name refused" &&
    cd "$tmp/zax-public" && git worktree remove --force "$tmp/wt-zax-redone" && git branch -qD wtb
commit a.txt 'fine\n' -m ok && git tag -a v1 -m 'Release' && tag=v1 && run 0 "clean annotated tag"
commit a.txt 'fine\n' -m ok && git -c user.name='Fnordel' tag -a v1 -m 'Release' && tag=v1 && expect="a private word" run 1 "tag: tagger name"
commit a.txt 'fine\n' -m ok && git tag -a v1 -m 'For plyrzork and Quxblorf' && tag=v1 && expect="a private word" run 1 "tag: message"
commit a.txt 'fine\n' -m ok && git -c user.email="somebody${at}mail.invalid" tag -a v1 -m 'Release' && tag=v1 && expect="other than a GitHub noreply" run 1 "tag: tagger e-mail"
# what the remote already has is not checked again (unless ZAX_PREPUSH_ALL=1); a new branch is checked against it
git init -q --bare "$tmp/remote.git" && git remote add origin "$tmp/remote.git"
commit a.txt 'QVMH-01\n' -m 'old' && git push -q --no-verify origin HEAD:refs/heads/main && pushed=$(git rev-parse HEAD)
base=$pushed
commit b.txt 'fine\n' -m 'Clean' && run 0 "new branch on top of what the remote has" "$zero"
commit b.txt 'fine\n' -m 'Clean' && hookenv=ZAX_PREPUSH_ALL=1 expect="a VM name" run 1 "ZAX_PREPUSH_ALL=1 checks the whole history" "$zero"
commit b.txt 'fine\n' -m 'Clean' && run 0 "unknown old remote value: the remote's refs still exclude what it has" 1111111111111111111111111111111111111111
# the file is required
commit a.txt 'fine\n' -m ok && hookenv="ZAX_LOCAL_JSON=$tmp/missing.json" expect="not found" run 1 "local.json missing"
commit a.txt 'fine\n' -m ok && hookenv="ZAX_LOCAL_JSON=$tmp/nowords.json" expect="no \"private_words\"" run 1 "local.json without private_words"
# zax-redone and zax-testtools may name the VMs, nothing else
setup zax-redone
commit a.txt 'QVMH-01 and QVMC-02\n' -m 'Seen on QVMX-09' && run 0 "private repository: VM names"
commit a.txt 'qvmh-01 and Qvmc-02\n' -m 'Seen on qvmx-09' && run 0 "private repository: VM names in another case"
commit a.txt 'QSHR-01\n' -m ok && expect="test setup" run 1 "private repository: share prefix"
commit a.txt 'fine\n' -m 'Quxblorf' && expect="a private word" run 1 "private repository: private word"

# zax-decomp's exemption covers its published objects by SHA-1 only: a new commit with a VM name is refused there
setup zax-decomp
commit a.txt 'QVMH-01\n' -m 'Seen on QVMC-01' && expect="a VM name" run 1 "zax-decomp: a new commit with VM names (review4 F4)"
# zax-editor's and zax-formats' exemptions (their published CLAUDE.md blobs) do not reach new objects either
setup zax-editor
commit CLAUDE.md 'on QVMH-01\n' -m ok && expect="a VM name" run 1 "zax-editor: a new CLAUDE.md with a VM name"
setup zax-formats
commit CLAUDE.md 'on QVMC-02\n' -m ok && expect="a VM name" run 1 "zax-formats: a new CLAUDE.md with a VM name"
# the README screenshots of zax-launcher and zax-editor (docs/images/) are allowed, other folders not
setup zax-launcher
commit docs/images/start.png '\211PNG\r\n\032\n\000' -m ok && run 0 "zax-launcher: docs/images/*.png allowed"
commit docs/other/start.png '\211PNG\r\n\032\n\000' -m ok && expect="an image outside" run 1 "zax-launcher: an image elsewhere"
commit docs/images/start.png '\211PNG\r\n\032\nQuxblorf\000' -m ok && expect="a private word" run 1 "zax-launcher: an allowed image is still scanned"

[ "$fails" -eq 0 ] && echo "all cases as expected" || echo "$fails case(s) failed"
[ "$fails" -eq 0 ]
