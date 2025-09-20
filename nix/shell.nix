{pkgs ? import <nixpkgs> {}}:
pkgs.mkShell {
  buildInputs = with pkgs; [
    python313
    python313Packages.pip
    uv
    ruff
    gcc
    pkg-config
  ];
  env = {
    LD_LIBRARY_PATH = with pkgs;
      lib.makeLibraryPath [
        stdenv.cc.cc
      ];
  };

  shellHook = ''
    # Set locale to avoid Python locale warnings
    export LOCALE_ARCHIVE="${pkgs.glibcLocales}/lib/locale/locale-archive"
    export LC_ALL="C.UTF-8"
  '';
}
