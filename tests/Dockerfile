FROM oraclelinux:8

MAINTAINER Michael Simacek <michael.simacek@oracle.com>

ENV LANG=en_US.UTF-8 \
    PS1='\w\$ '

# Add RabbitMQ-Metadata for the yum Package Manager
COPY rabbitmq.repo /etc/yum.repos.d/

# LLVM version 14 is needed by llvmlite, see https://github.com/numba/llvmlite/issues/914 for llvm 15 support
# We downgrade rust because of LLVM
RUN dnf install -y \
        oracle-software-release-el8 \
        oracle-epel-release-el8 \
        oraclelinux-developer-release-el8 \
        oracle-instantclient-release-el8 \
        mysql-release-el8 \
    && dnf config-manager --add-repo https://yum.oracle.com/repo/OracleLinux/OL8/codeready/builder/x86_64 \
    && dnf module install -y nodejs:16-epel/default \
    && dnf --setopt=obsoletes=0 install -y \
        'clang-devel-14.*.x86_64' \
        'llvm-devel-14.*.x86_64' \
        'llvm-toolset-14.*.x86_64' \
        'rust-1.62.*.x86_64' \
        atlas \
        autoconf \
        automake \
        bcftools \
        bzip2 \
        bzip2-devel \
        cairo-devel \
        cairo-gobject-devel \
        cargo \
        cmake \
        curl \
        ed \
        figlet \
        file \
        fish \
        flac-devel \
        fluidsynth-devel \
        freetype-devel \
        gcc \
        gcc-c++ \
        gcc-gfortran \
        gdbm-devel \
        geos-devel \
        ghostscript \
        git \
        git-daemon \
        gobject-introspection-devel \
        graphviz-devel \
        gtk3-devel \
        hdf5-devel \
        htslib-tools \
        iproute \
        java-11-openjdk-devel.x86_64 \
        java-11-openjdk-jmods.x86_64 \
        jq \
        lcms2-devel \
        libX11-devel \
        libXext-devel \
        libarchive-devel \
        libatomic \
        libcurl-devel \
        libffi-devel \
        libglvnd-egl \
        libglvnd-glx \
        libimagequant-devel \
        libjpeg-turbo-devel \
        libmemcached-devel \
        libmodplug-devel \
        libraqm-devel \
        libtiff-devel \
        libtool \
        libwebp-devel \
        libxcb-devel \
        libxkbcommon \
        libxml2-devel \
        libxslt-devel \
        libyaml-devel \
        make \
        mercurial \
        mpich-devel \
        mysql-devel \
        mysql-server \
        ncurses-devel \
        netcdf-devel \
        nmap-ncat \
        openblas-devel \
        openjpeg2-devel \
        openmpi \
        openmpi-devel \
        openssl \
        openssl-devel \
        opusfile-devel \
        oracle-instantclient-basic \
        pandoc \
        patch \
        patchelf \
        portaudio-devel \
        portmidi-devel \
        postgresql-contrib \
        postgresql-devel \
        postgresql-odbc \
        postgresql-server \
        protobuf-devel \
        python3 \
        python3-oci-cli \
        qt5-qtbase-devel \
        qt5-qtbase-gui \
        qt5-qtbase-private-devel \
        rabbitmq-server \
        readline-devel \
        redis \
        rsync \
        samtools \
        sqlite-devel \
        tar \
        tcsh \
        tesseract \
        time \
        tk-devel \
        unixODBC-devel \
        unzip \
        vim \
        wget \
        which \
        xcb-util-cursor \
        xorg-x11-server-Xvfb \
        xz \
        xz-devel \
        yasm \
        zeromq-devel \
        zip \
        zlib-devel \
    && dnf clean all && rm -rf /var/cache/dnf

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk

ENV CPYTHON_VERSION_SHORT=3.10
ENV CPYTHON_VERSION=${CPYTHON_VERSION_SHORT}.8
ENV CPYTHON_PATH=/usr/local/bin/python${CPYTHON_VERSION_SHORT}
ENV PATH=/usr/lib64/openmpi/bin/:${PATH}

# Build CPython version that will be used for GraalPy comparison
RUN curl -L https://www.python.org/ftp/python/${CPYTHON_VERSION}/Python-${CPYTHON_VERSION}.tar.xz | \
    tar -xJ && \
    cd Python-${CPYTHON_VERSION} && \
    ./configure --enable-shared --enable-optimizations && \
    make all altinstall && \
    cd .. && \
    rm -r Python-${CPYTHON_VERSION}

# OL has split lib and lib64, but python by default installs into lib. This is desirable for us, because this layout
# propagates to virtualenvs. When virtualenvs have separate lib64, some packages that have fishy packaging, notably
# cuda libs, don't work.
RUN echo -e "/usr/local/lib\n/usr/local/lib64" > /etc/ld.so.conf.d/local-python-x86_64.conf && ldconfig && ${CPYTHON_PATH} --version

# Update CMake
ENV CMAKE_VERSION=3.25.3
RUN curl -L https://github.com/Kitware/CMake/releases/download/v${CMAKE_VERSION}/cmake-${CMAKE_VERSION}.tar.gz | tar -xz  && \
    cd cmake-${CMAKE_VERSION} && \
    cmake -B build -DCMAKE_BUILD_TYPE=Release && \
    cmake --build build && \
    cmake --install build && \
    cd .. && \
    rm -r cmake-${CMAKE_VERSION}

# Build SDL2 for testing pygame
ENV SDL_VERSION=2.26.2
RUN curl -L https://github.com/libsdl-org/SDL/releases/download/release-${SDL_VERSION}/SDL2-${SDL_VERSION}.tar.gz | tar -xz  && \
    cd SDL2-${SDL_VERSION} && \
    cmake -B build -DCMAKE_BUILD_TYPE=Release && \
    cmake --build build --parallel && \
    cmake --install build && \
    cd .. && \
    rm -r SDL2-${SDL_VERSION}

ENV SDL_TTF_VERSION=2.20.1
RUN curl -L https://github.com/libsdl-org/SDL_ttf/releases/download/release-${SDL_TTF_VERSION}/SDL2_ttf-${SDL_TTF_VERSION}.tar.gz | tar -xz  && \
    cd SDL2_ttf-${SDL_TTF_VERSION} && \
    cmake -B build -DCMAKE_BUILD_TYPE=Release && \
    cmake --build build --parallel && \
    cmake --install build && \
    cd .. && \
    rm -r SDL2_ttf-${SDL_TTF_VERSION}

ENV SDL_IMAGE_VERSION=2.6.2
RUN curl -L https://github.com/libsdl-org/SDL_image/releases/download/release-${SDL_IMAGE_VERSION}/SDL2_image-${SDL_IMAGE_VERSION}.tar.gz | tar -xz  && \
    cd SDL2_image-${SDL_IMAGE_VERSION} && \
    cmake -B build -DCMAKE_BUILD_TYPE=Release && \
    cmake --build build --parallel && \
    cmake --install build && \
    cd .. && \
    rm -r SDL2_image-${SDL_IMAGE_VERSION}

ENV SDL_MIXER_VERSION=2.6.2
RUN curl -L https://github.com/libsdl-org/SDL_mixer/releases/download/release-${SDL_MIXER_VERSION}/SDL2_mixer-${SDL_MIXER_VERSION}.tar.gz | tar -xz  && \
    cd SDL2_mixer-${SDL_MIXER_VERSION} && \
    cmake -B build -DCMAKE_BUILD_TYPE=Release && \
    cmake --build build --parallel && \
    cmake --install build && \
    cd .. && \
    rm -r SDL2_mixer-${SDL_MIXER_VERSION}

ENV PROJ_VERSION=9.1.1
RUN curl -L https://download.osgeo.org/proj/proj-${PROJ_VERSION}.tar.gz | tar -xz  && \
    cd proj-${PROJ_VERSION} && \
    mkdir build && \
    cd build && \
    cmake .. && \
    cmake --build . --parallel && \
    cmake --build . --target install && \
    cd ../.. && \
    rm -r proj-${PROJ_VERSION}

# For rasterio
ENV GDAL_VERSION=3.6.1
RUN curl -L https://github.com/OSGeo/gdal/releases/download/v${GDAL_VERSION}/gdal-${GDAL_VERSION}.tar.gz | tar -xz  && \
    cd gdal-${GDAL_VERSION} && \
    cmake -B build -DCMAKE_BUILD_TYPE=Release && \
    cmake --build build && \
    cmake --install build && \
    cd .. && \
    rm -r gdal-${GDAL_VERSION}

ENV LIBRDKAFKA_VERSION=2.0.2
RUN curl -L https://github.com/confluentinc/librdkafka/archive/refs/tags/v${LIBRDKAFKA_VERSION}.tar.gz | tar -xz  && \
    cd librdkafka-${LIBRDKAFKA_VERSION} && \
    ./configure && \
    make -j 8 && \
    make install && \
    cd .. && \
    rm -r librdkafka-${LIBRDKAFKA_VERSION}

ENV NINJA_VERSION=1.11.1
# TODO: What did they patch here?
# COPY ./ninja.patch ninja.patch
RUN curl -L https://github.com/ninja-build/ninja/archive/refs/tags/v${NINJA_VERSION}.tar.gz | tar -xz  && \
    cd ninja-${NINJA_VERSION} && \
    # patch -p1 < ../ninja.patch && \
    cmake -B build -DCMAKE_BUILD_TYPE=Release && \
    cmake --build build && \
    cmake --install build && \
    cd .. && \
    rm -r ninja-${NINJA_VERSION}

ENV ARROW_VERSION=12.0.1
RUN curl -L https://github.com/apache/arrow/archive/refs/tags/apache-arrow-${ARROW_VERSION}.tar.gz | tar -xz && \
    cd arrow-apache-arrow-${ARROW_VERSION}/cpp && \
    cmake -B build -DCMAKE_BUILD_TYPE=Release -DARROW_COMPUTE=ON -DARROW_CSV=ON -DARROW_JSON=ON -DARROW_FILESYSTEM=ON -DARROW_DATASET=ON && \
    cmake --build build && \
    cmake --install build && \
    cd ../.. && \
    rm -r arrow-apache-arrow-${ARROW_VERSION}

RUN ldconfig

# Install bazelisk for fetching bazel
ENV USE_BAZEL_FALLBACK_VERSION=silent:6.0.0
RUN curl -L https://github.com/bazelbuild/bazelisk/releases/download/v1.15.0/bazelisk-linux-amd64 -o /usr/local/bin/bazel && \
    chmod 755 /usr/local/bin/bazel

#### Runner setup
ENV WORK_DIR=/workdir

#### Python setup
ENV GRAALPY_HOME=/opt/graalpy

### Installing GraalPy
ENV GRAALPY_VERSION=23.1.1
RUN curl -sL -O https://github.com/oracle/graalpython/releases/download/graal-${GRAALPY_VERSION}/graalpy-community-${GRAALPY_VERSION}-linux-amd64.tar.gz ^ \
    tar --strip-components=1 -xzf graalpy-community-${GRAALPY_VERSION}-linux-amd64.tar.gz && \
    ln -s ${GRAALPY_HOME}/bin/graalpy /usr/local/bin/graalpy && \
    ln -s ${GRAALPY_HOME}/languages/python/graalpy_virtualenv /opt/graalpy_virtualenv

# Some packages use stdlib test files for testing, which GraalPy doesn't ship. Just symlink them for now
RUN rm -rf ${GRAALPY_HOME}/languages/python/lib/python3.*/test && \
    ln -s /usr/local/lib/python${CPYTHON_VERSION_SHORT}/test/ ${GRAALPY_HOME}/languages/python/lib/python3.*/

### User setup
RUN useradd -d "$WORK_DIR" -s /bin/bash tester
USER tester
WORKDIR /workdir
RUN git config --global user.name "GraalPy Tester"
RUN git config --global user.email "tester@graalpy.org"

# Prebuild numpy into the cache, everything needs it. But don't fail the build if it fails
# We prebuild matplotlib because it downloads stuff from sourceforge and sourceforge is impossible to reliably
# whitelist in the cluster because they keep adding mirrors all the time
ARG PREBUILD_NUMPY=''
RUN if [ -n "${PREBUILD_NUMPY}" ]; then \
    graalpy -m venv prebuild-venv && \
    prebuild-venv/bin/pip wheel numpy; \
    prebuild-venv/bin/pip wheel oldest-supported-numpy; \
    prebuild-venv/bin/pip wheel matplotlib; \
    true ; \
    fi
