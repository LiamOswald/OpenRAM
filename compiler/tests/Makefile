TOP_DIR := $(realpath $(dir $(lastword $(MAKEFILE_LIST)))../..)
include $(TOP_DIR)/openram.mk

.DEFAULT_GOAL := all

ARGS ?=
TEST_TECHS ?= scn4m_subm freepdk45
TECHS ?= scn4m_subm freepdk45 sky130

TEST_DIR   = $(TOP_DIR)/compiler/tests
TEST_SRCS  = $(sort $(notdir $(wildcard $(TEST_DIR)/*_test.py)))
TEST_BASES = $(basename $(TEST_SRCS))
TEST_STAMPS= $(addsuffix .ok,$(TEST_BASES))

OPENRAM_DIR = /openram/compiler/tests
RESULTS_DIR = $(OPENRAM_DIR)/results

# Use % for all techs: 
# %/test.py
# or a specific tech:
# freepdk45/test.py
BROKEN_STAMPS = \
	sky130/01_library_test.ok \
	sky130/04_column_mux_pbitcell_test.ok \
	sky130/04_dummy_pbitcell_test.ok \
	sky130/04_pbitcell_test.ok \
	sky130/04_pnand4_test.ok \
	sky130/04_pand4_test.ok \
	sky130/04_precharge_pbitcell_test.ok \
	sky130/04_replica_pbitcell_test.ok \
	sky130/05_pbitcell_array_test.ok \
	sky130/05_bitcell_array_test.ok \
	sky130/05_bitcell_array_1rw_1r_test.ok \
	sky130/05_dummy_array_test.ok \
	%/06_hierarchical_decoder_4096row_test.ok \
	sky130/07_column_mux_array_pbitcell_test.ok \
	sky130/19_pmulti_bank_test.ok \
	sky130/19_psingle_bank_test.ok \
	sky130/19_bank_select_pbitcell_test.ok \
	%/19_single_bank_16mux_1rw_1r_test.ok \
	%/19_single_bank_16mux_test.ok \
	%/20_sram_1bank_16mux_1rw_1r_test.ok \
	%/20_sram_1bank_16mux_test.ok \
	%/20_psram_1bank_2mux_1rw_1w_test.ok \
	%/20_psram_1bank_2mux_1rw_1w_wmask_test.ok \
	%/20_psram_1bank_2mux_1w_1r_test.ok \
	%/20_psram_1bank_2mux_test.ok \
	%/21_hspice_delay_test.ok \
	%/21_hspice_setuphold_test.ok \
	sky130/20_psram_1bank_4mux_1rw_1r_test.ok \
	sky130/22_psram_1bank_2mux_func_test.ok \
	sky130/22_psram_1bank_4mux_func_test.ok \
	sky130/22_psram_1bank_8mux_func_test.ok \
	sky130/22_psram_1bank_nomux_func_test.ok \
	%/22_psram_1bank_2mux_func_test.ok \
	%/22_psram_1bank_4mux_func_test.ok \
	%/22_psram_1bank_8mux_func_test.ok \
	%/22_psram_1bank_nomux_func_test.ok \
	%/22_sram_1bank_2mux_func_test.ok \
	%/22_sram_1bank_2mux_global_func_test.ok \
	%/22_sram_1bank_2mux_sparecols_func_test.ok \
	%/22_sram_1bank_4mux_func_test.ok \
	%/22_sram_1bank_8mux_func_test.ok \
	%/22_sram_1bank_nomux_1rw_1r_func_test.ok \
	%/22_sram_1bank_nomux_func_test.ok \
	%/22_sram_1bank_nomux_sparecols_func_test.ok \
	%/22_sram_1bank_wmask_1rw_1r_func_test.ok \
	%/22_sram_wmask_func_test.ok \
	sky130/23_lib_sram_linear_regression_test.ok \
	sky130/23_lib_sram_model_corners_test.ok \
	sky130/23_lib_sram_model_test.ok \
	sky130/23_lib_sram_prune_test.ok \
	sky131/23_lib_sram_test.ok \
	%/26_hspice_pex_pinv_test.ok \
	%/27_verilog_multibank_test.ok \
	%/50_riscv_1k_1rw1r_func_test.ok \
	%/50_riscv_1k_1rw_func_test.ok \
	%/50_riscv_1rw1r_func_test.ok \
	%/50_riscv_1rw1r_phys_test.ok \
	%/50_riscv_1rw_func_test.ok \
	%/50_riscv_1rw_phys_test.ok \
	%/50_riscv_2k_1rw1r_func_test.ok \
	%/50_riscv_2k_1rw_func_test.ok \
	%/50_riscv_4k_1rw1r_func_test.ok \
	%/50_riscv_4k_1rw_func_test.ok \
	%/50_riscv_512b_1rw1r_func_test.ok \
	%/50_riscv_512b_1rw_func_test.ok \
	%/50_riscv_8k_1rw1r_func_test.ok \
	%/50_riscv_8k_1rw_func_test.ok

gettech = $(word 1,$(subst /, ,$*))
getfile = $(word 2,$(subst /, ,$*))
TECH_TEST_STAMPS=$(foreach T, $(TEST_TECHS), $(addprefix $T/, $(TEST_STAMPS)))

# Filter out the tests after creating the tech stamps
WORKING_TECH_TEST_STAMPS=$(shell shuf -e -- $(filter-out $(BROKEN_STAMPS), $(TECH_TEST_STAMPS)))


# Run all technologies
all: clean $(WORKING_TECH_TEST_STAMPS)
	@ls -1 $(TOP_DIR)/compiler/tests/results/*/*.bad 1> /dev/null 2>&1 && echo "FAILING TESTS" && ls -1 $(TOP_DIR)/compiler/tests/results/*/*.bad | sed -e "s#^.*results\/##" && exit 1 || exit 0
.PHONY: all

# Run a given technology
# e.g. make freepdk45
$(TECHS): 
	@$(MAKE) --no-print-directory $(filter-out $(BROKEN_STAMPS), $(addprefix $@/, $(TEST_STAMPS)))
.PHONY: $(TECHS)

# Targets for each individual test in all technologies
# e.g. make 04_pinv_1x_test
$(TEST_BASES):
	@$(MAKE) --no-print-directory $(foreach T, $(TECHS), $(addprefix $T/, $@.ok))
.PHONY: $(TEST_BASES)

# To run a test in a given technology
%.ok: 
#	@echo "Running $(gettech) $(getfile) ... "
	@rm -rf results/$*
	@rm -rf results/$*.*
	@mkdir -p results/$*/tmp
	@$(DOCKER_CMD) sh -c ". /home/cad-user/.bashrc && sleep 1 && python3 -u $(OPENRAM_DIR)/$(getfile).py \
		-t $(gettech) -k -v $(ARGS) -p $(OPENRAM_DIR)/results/$* > $(OPENRAM_DIR)/results/$*.out 2>&1 && touch $(OPENRAM_DIR)/results/$*.ok || touch $(OPENRAM_DIR)/results/$*.bad"
ifdef KEEP
	@test -f $(TOP_DIR)/compiler/tests/results/$*.ok && echo "$* ... PASS!" || echo "$* ... FAIL!"
else
	@test -f $(TOP_DIR)/compiler/tests/results/$*.ok && echo "$* ... PASS!" && rm -rf $(TOP_DIR)/compiler/tests/results/$* || echo "$* ... FAIL!"
endif
.DELETE_ON_ERROR: $(TEST_STAMPS)

.PHONY: docker-pull
docker-pull:
	docker pull vlsida/openram-ubuntu:latest

clean:
	@rm -rf $(TOP_DIR)/compiler/tests/results
.PHONE: clean
