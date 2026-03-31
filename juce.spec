%define	oname	JUCE

# FIXME: ATM building examples fails (linking errors for libpng and libjpeg)
%bcond_with	examples
%bcond_without	docs

Summary:		Open-source cross-platform C++ application framework 
Name:	juce
Version:		8.0.12
Release:		1
License:		GPLv3+
Group:	Sound
Url:		https://juce.com/
Source0:	https://github.com/juce-framework/JUCE/archive/refs/tags/%{oname}-%{version}.tar.gz
Source1:	juce_VSTInterface.h
Source2:	%{name}.png
Source100:	juce.rpmlintrc
Patch0:	juce-8.0.12-fix-install-paths.patch
Patch1:	juce-8.0.12-projucer-disable-update-check.patch
Patch2:	juce-8.0.12-projucer-fix-juce-paths.patch
Patch3:	juce-8.0.12-use-system-libs.patch
Patch4:	juce-8.0.12-fix-example-linking.patch
BuildRequires:  cmake >= 3.22
BuildRequires:  doxygen
BuildRequires:  graphviz
BuildRequires:  make
BuildRequires:  python
BuildRequires:  ladspa-devel
BuildRequires:  pkgconfig(alsa)
BuildRequires:  pkgconfig(fftw3) >= 3.3.5
BuildRequires:  pkgconfig(flac)
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:  pkgconfig(gl)
BuildRequires:  pkgconfig(glu)
BuildRequires:  pkgconfig(jack)
BuildRequires:  pkgconfig(libcurl)
BuildRequires:  pkgconfig(liblo)
BuildRequires:  pkgconfig(libjpeg)
BuildRequires:  pkgconfig(libpng)
BuildRequires:  pkgconfig(lv2)
BuildRequires:  pkgconfig(samplerate)
BuildRequires:  pkgconfig(vorbis)
BuildRequires:  pkgconfig(vorbisenc)
BuildRequires:  pkgconfig(vorbisfile)
BuildRequires:  pkgconfig(vst3sdk)
BuildRequires:  pkgconfig(webkit2gtk-4.1)
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xcomposite)
BuildRequires:  pkgconfig(xcursor)
BuildRequires:  pkgconfig(xext)
BuildRequires:  pkgconfig(xinerama)
BuildRequires:  pkgconfig(xrandr)
BuildRequires:  pkgconfig(xrender)
BuildRequires:  pkgconfig(zlib)

%description
This is an open-source cross-platform C++ application framework for creating
high quality desktop and mobile applications, including VST, VST3, AU, AUv3,
AAX and LV2 audio plug-ins and plug-in hosts. It can be easily integrated with
existing projects via CMake, or can be used as a project generation tool via
the Projucer program.

%files
%license LICENSE.md
%doc README.md CHANGE_LIST.md BREAKING_CHANGES.md
%{_bindir}/%{oname}-%{version}/%{name}_lv2_helper
#{_bindir}/%%{oname}-%%{version}/%%{name}_vst3_helper
%{_bindir}/juceaide
%dir %{_libdir}/cmake/%{oname}-%{version}
%{_libdir}/cmake/%{oname}-%{version}/*
%dir %{_datadir}/%{name}/modules
%{_datadir}/%{name}/modules/*
%{_iconsdir}/hicolor/*/apps/%{name}.png

#-----------------------------------------------------------------------------

%package	-n projucer
Summary: IDE to create JUCE projects
Group:	Development/Other
Requires:	%{name} = %{EVRD}
Provides:	%{name}-projucer = %{EVRD}

%description -n projucer
The Projucer program can then be used to create new JUCE projects, view
tutorials and run examples. .It supports exporting projects for Xcode (macOS
and iOS), Visual Studio, Android Studio, Code::Blocks and Linux Makefiles as
well as containing a source code editor.

%files -n projucer
%{_bindir}/Projucer
%{_datadir}/applications/com.%{name}-projucer.desktop
%{_iconsdir}/hicolor/512x512/apps/Projucer.png

#-----------------------------------------------------------------------------

%if %{with docs}
%package docs
Summary:	Docs for %{name}
Group:	Documentation

%description docs
Development documentation for %{name}.

%files docs
%{_docdir}/%{name}/html/
%endif

#-----------------------------------------------------------------------------

%if %{with examples}
%package examples
Summary:	Juce examples and utilities
Group:	Sound
Requires:	%{name} = %{version}-%{release}
Provides:	%{name}-examples = %{version}-%{release}

%description examples
Example projects built with %{name}; among them:
* AudioAppDemo.
* AudioRecordingDemo.
* MidiDemo.
* SimpleFFTDemo.
* AudioLatencyDemo.
* AudioSettingsDemo.
* MPEDemo.
* AudioPlaybackDemo.
* AudioSynthesiserDemo.
* PluckedStringsDemo.
* DemoRunner.

%files examples
%{_datadir}/%{name}/examples/Audio/
%{_datadir}/%{name}/examples/DemoRunner/
%{_datadir}/%{name}/examples/DSP/
%{_datadir}/%{name}/examples/GUI/
%{_datadir}/%{name}/examples/Plugins/
%{_datadir}/%{name}/examples/Utilities/
%endif

#-----------------------------------------------------------------------------

%prep
%autosetup -p1 -n %{oname}-%{version}

# Fix perms
find -type f -exec chmod 0644 {} \;

# Drop bundled source for stuff we have on system
rm -rvf modules/juce_audio_formats/codecs/flac/ \
		modules/juce_audio_formats/codecs/oggvorbis/ \
		modules/juce_graphics/image_formats/jpglib/ \
		modules/juce_graphics/image_formats/pnglib/ \
		modules/juce_audio_plugin_client/AU/ \
		modules/juce_core/zip/zlib/


    
%build
export CFLAGS="%{optflags} -fcommon"
# Make sure we link with the system libraries
export LDFLAGS="%{ldflags} -L/usr/lib64/libglvnd/ -lpng16 -ljpeg -lFLAC -lvorbis -lvorbisfile -lvorbisenc -logg -lz"
%cmake -DCMAKE_BUILD_TYPE=Release \
	-DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DJUCE_BUILD_EXTRAS=ON \
%if %{with examples}
	-DJUCE_BUILD_EXAMPLES=ON \
%else
	-DJUCE_BUILD_EXAMPLES=OFF \
%endif
	-DJUCE_TOOL_INSTALL_DIR=bin \
    -DJUCER_ENABLE_GPL_MODE=ON \
	-DCMAKE_SKIP_RPATH=ON \
    -Wno-dev

%make_build

%if %{with docs}
# Also build the devel docs
pushd ../docs/doxygen
	python build.py
	#doxygen Doxyfile
popd
%endif


%install
%make_install -C build

## Install custom vst2 handling from juce < 5.4.1
install -vDm 644 %{SOURCE1} -t %{buildroot}%{_datadir}/%{name}/modules/juce_audio_processors/format_types/

## Projucer has no install target: go manually - need JUCE_BUILD_EXTRAS enabled
pushd build/extras/Projucer/Projucer_artefacts/Release
	install -vDm 755 Projucer -t %{buildroot}%{_bindir}
popd

# Provide a .desktop file for projucer
mkdir -p %{buildroot}%{_datadir}/applications
cat <<EOF > %{buildroot}%{_datadir}/applications/com.%{name}-projucer.desktop
[Desktop Entry]
Name=Projucer
GenericName=Code manager and editor
Comment=Cross-platform project manager and C++ code editor for Plugins
Categories=GTK;Development;
Exec=Projucer
Icon=%{name}
StartupNotify=true
Terminal=false
Type=Application
EOF

#  Install icons for Projucer...
install -d -m 0755 %{buildroot}%{_iconsdir}
install -vDm 644 examples/Assets/juce_icon.png %{buildroot}%{_iconsdir}/hicolor/512x512/apps/Projucer.png
# ... and for %%{name}
for i in 16 32 48 72 96 128 256; do
install -d -m 0755 %{buildroot}%{_iconsdir}/hicolor/${i}x${i}/apps
install -m 0644 %{SOURCE2} %{buildroot}%{_iconsdir}/hicolor/${i}x${i}/apps/%{name}.png
convert -resize ${i}x${i} %{buildroot}%{_iconsdir}/hicolor/${i}x${i}/apps/%{name}.png %{buildroot}%{_iconsdir}/hicolor/${i}x${i}/apps/%{name}.png
done

%if %{with docs}
## Install built docs
install -vDm 644 ./*.txt -t %{buildroot}%{_docdir}/%{name}/
install -d -m 0755 %{buildroot}%{_docdir}/%{name}/html
cp -af %{_builddir}/JUCE-%{version}/docs/doxygen/doc/* %{buildroot}%{_docdir}/%{name}/html/
%endif

%if %{with examples}
## Make examples and .h .cpp available in package examples
mkdir -p %{buildroot}%{_datadir}/%{name}/examples/{Audio,DemoRunner,DSP,GUI,Plugins,Utilities}
if [ -d %{_builddir}/JUCE-%{version}/build/examples ]; then
	cd %{_builddir}/JUCE-%{version}/build/examples
	for i in `find -type f -iname *Demo -o -iname *.h -o -iname *.cpp`; do
		dird=`echo $i | cut -d'/' -f2-3 | cut -d_ -f1`
		mkdir -p %{buildroot}%{_datadir}/%{name}/examples/$dird
		cp -f $i %{buildroot}%{_datadir}/%{name}/examples/$dird
	done
fi
%endif

# Unwanted stuff
rm -f %{buildroot}%{_docdir}/%{name}/CMakeLists.txt
find %{buildroot}%{_datadir}/%{name}/modules -name ".clang-tidy" -delete
