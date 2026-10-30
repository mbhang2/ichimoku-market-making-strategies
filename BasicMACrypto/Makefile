ifdef INTEL
    CC=icc
else
    CC=g++
endif

ifdef DEBUG
    CFLAGS=-c -g -fPIC -fpermissive -std=c++11
else
    CFLAGS=-c -fPIC -fpermissive -O3 -std=c++11
endif

ifneq ($(LOGGING),)
    CFLAGS += -DLOGGING=$(LOGGING)
endif

# Shortwindow, MediumWindow, and LongWindow are the three parameters for the strategy.
# They are defined here and can be changed as per the user's requirement.
# CFLAGS += -DShortWindow=9 -DMediumWindow=26 -DLongWindow=52
# Check if all variables are defined
ifdef ShortWindow
  ifdef MediumWindow
    ifdef LongWindow
		CFLAGS += -DShortWindow=\"$(ShortWindow)\" -DMediumWindow=\"$(MediumWindow)\" -DLongWindow=\"$(LongWindow)\"
    endif
  endif
endif

Aggression ?= 1

ifdef Aggression
	CFLAGS += -DAggression=\"$(Aggression)\"
endif

AggressionMultiplier ?= 0.01

ifdef AggressionMultiplier
	CFLAGS += -DAggressionMultiplier=$(AggressionMultiplier)
endif

SpreadTick ?= 0.11

ifdef SpreadTick
	CFLAGS += -DSpreadTick=$(SpreadTick)
endif


PrintDebugInfo ?= 0

ifdef PrintDebugInfo
	CFLAGS += -DPrintDebugInfo=$(PrintDebugInfo)
endif

BasicMACryptoDebugMessages ?= 0

ifdef BasicMACryptoDebugMessages
	CFLAGS += -DBasicMACryptoDebugMessages=$(BasicMACryptoDebugMessages)
endif



USERNAME=$(shell whoami)
LIBPATH=../../../../libs/x64
INCLUDEPATH=../../../../includes
INCLUDE_GROUP_02_LIBS=../includes
INCLUDES=-I/usr/include -I$(INCLUDEPATH) -I$(INCLUDE_GROUP_02_LIBS)
LDFLAGS=$(LIBPATH)/libstrategystudio_analytics.a $(LIBPATH)/libstrategystudio.a $(LIBPATH)/libstrategystudio_transport.a $(LIBPATH)/libstrategystudio_marketmodels.a $(LIBPATH)/libstrategystudio_utilities.a $(LIBPATH)/libstrategystudio_flashprotocol.a

INSTANCE_NAME=BasicMACrypto# single word, no special characters
STRATEGY_NAME=BasicMACrypto# should be your cpp file name, single word, no special characters
# START_DATE=2021-11-05# for your backtest
# END_DATE=2021-11-05# for your backtest

# CFLAGS += -DINSTANCE_NAME=$(INSTANCE_NAME) -DSTRATEGY_NAME=$(STRATEGY_NAME) -DSTART_DATE=$(START_DATE) -DEND_DATE=$(END_DATE)
CFLAGS += -DINSTANCE_NAME=\"$(INSTANCE_NAME)\" -DSTRATEGY_NAME=\"$(STRATEGY_NAME)\" -DSTART_DATE=\"$(START_DATE)\" -DEND_DATE=\"$(END_DATE)\"

# Define the names of the library, source, and header files.
LIBRARY=BasicMACrypto.so
SOURCES=BasicMACrypto.cpp
HEADERS=BasicMACrypto.h 

OBJECTS=$(SOURCES:.cpp=.o)

.PHONY: all make_executable delete_instance clean_dlls move_strategy_dll build_strategy run_backtest

all: clean $(HEADERS) $(LIBRARY)

$(LIBRARY) : $(OBJECTS)
	$(CC) -shared -Wl,-soname,$(LIBRARY).1 -o $(LIBRARY) $(OBJECTS) $(LDFLAGS)
	
.cpp.o: $(HEADERS)
	$(CC) $(CFLAGS) $(INCLUDES) $< -o $@

clean:
	rm -rf *.o $(LIBRARY)

# find_and_replace:
# 	@echo "Adding correct addresses according to the user..."
# 	chmod +x ./provision_scripts/config_user.sh
# 	./provision_scripts/config_user.sh

git_pull:
	@echo "Compiling Strategy for $(USERNAME)..."
	chmod +x ./provision_scripts/git_pull.sh
	./provision_scripts/git_pull.sh
	chmod +x ./provision_scripts/config_user.sh
	./provision_scripts/config_user.sh

make_executable: git_pull
	chmod +x ./provision_scripts/*.sh
	chmod +x ./provision_scripts/*.py
	ls -l ./provision_scripts/

delete_instance: make_executable
	pypy3 ./provision_scripts/delete_instance.py "$(INSTANCE_NAME)" "$(STRATEGY_NAME)"

clean_dlls:
ifeq ($(USERNAME), ashitabh)
	mkdir -p /home/ashitabh/Documents/ss/bt/strategies_dlls
	rm -rf /home/ashitabh/Documents/ss/bt/strategies_dlls/*
else ifeq ($(USERNAME), akshay)
	mkdir -p /media/akshay/Data/ss/bt/strategies_dlls
	rm -rf /media/akshay/Data/ss/bt/strategies_dlls/*
else ifeq ($(USERNAME), vagrant)
	mkdir -p /home/vagrant/ss/bt/strategies_dlls
	rm -rf /home/vagrant/ss/bt/strategies_dlls/*
endif
	

move_strategy_dll: delete_instance clean_dlls all
ifeq ($(USERNAME), ashitabh)
	cp $(LIBRARY) /home/ashitabh/Documents/ss/bt/strategies_dlls/.
else ifeq ($(USERNAME), akshay)
	cp $(LIBRARY) /media/akshay/Data/ss/bt/strategies_dlls/.
else ifeq ($(USERNAME), vagrant)
	cp $(LIBRARY) /home/vagrant/ss/bt/strategies_dlls/.
endif

build_strategy: move_strategy_dll
	./provision_scripts/build_strategy.sh "$(INSTANCE_NAME)" "$(STRATEGY_NAME)" "$(START_DATE)" "$(END_DATE)"

run_backtest: build_strategy
	chmod +x ./provision_scripts/run_backtest.sh
ifeq ($(USERNAME), ashitabh)
	@echo "Activating fin556_env for Ashitabh"
	@bash -c "source ~/Documents/fin556_env/bin/activate"
endif
	./provision_scripts/run_backtest.sh "$(INSTANCE_NAME)" "$(START_DATE)" "$(END_DATE)" "$(STRATEGY_NAME)"