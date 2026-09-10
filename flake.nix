{
  description = "Coptic typefaces revived from printed books: Layton Coptic and Lambdin Coptic";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAll = f: nixpkgs.lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});

      # A face is the committed OTF/TTF plus its specimen and README; nothing is built.
      mkFace = pkgs: { pname, version, face, description }:
        pkgs.stdenvNoCC.mkDerivation {
          inherit pname version;
          src = ./faces + "/${face}";
          dontBuild = true;
          installPhase = ''
            install -Dm444 *.otf -t $out/share/fonts/opentype
            install -Dm444 *.ttf -t $out/share/fonts/truetype
            install -Dm444 specimen.pdf README.md -t $out/share/doc/${pname}
          '';
          meta = {
            inherit description;
            homepage = "https://github.com/kmein/coptic-fonts";
            platforms = pkgs.lib.platforms.all;
          };
        };
    in {
      packages = forAll (pkgs: rec {
        layton-coptic = mkFace pkgs {
          pname = "layton-coptic"; version = "1.3"; face = "layton";
          description = "Revival of the Coptic type in Bentley Layton's A Coptic Grammar (2000)";
        };
        lambdin-coptic = mkFace pkgs {
          pname = "lambdin-coptic"; version = "1.0"; face = "lambdin";
          description = "Revival of the typewriter Coptic in Lambdin's Introduction to Sahidic Coptic (1983)";
        };
        default = pkgs.symlinkJoin {
          name = "coptic-fonts";
          paths = [ layton-coptic lambdin-coptic ];
        };
      });

      # Everything the pipeline in src/ needs to rebuild a face from page scans.
      devShells = forAll (pkgs: {
        default = pkgs.mkShell {
          packages = with pkgs; [
            (python3.withPackages (ps: with ps; [ pillow numpy scipy fonttools ]))
            poppler-utils potrace fontforge typst imagemagick
          ];
          shellHook = ''
            echo "coptic-font: FACE=layton|lambdin, run src/ from the repo root; see README.md"
          '';
        };
      });
    };
}
