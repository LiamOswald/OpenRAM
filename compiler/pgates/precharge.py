# See LICENSE for licensing information.
#
# Copyright (c) 2016-2019 Regents of the University of California and The Board
# of Regents for the Oklahoma Agricultural and Mechanical College
# (acting for and on behalf of Oklahoma State University)
# All rights reserved.
#
import contact
import design
import debug
from tech import parameter
from vector import vector
from globals import OPTS
from sram_factory import factory
from tech import drc


class precharge(design.design):
    """
    Creates a single precharge cell
    This module implements the precharge bitline cell used in the design.
    """
    def __init__(self, name, size=1, bitcell_bl="bl", bitcell_br="br"):

        debug.info(2, "creating precharge cell {0}".format(name))
        design.design.__init__(self, name)

        self.bitcell = factory.create(module_type="bitcell")
        self.beta = parameter["beta"]
        self.ptx_width = self.beta * parameter["min_tx_size"]
        self.width = self.bitcell.width
        self.bitcell_bl = bitcell_bl
        self.bitcell_br = bitcell_br
        self.bitcell_bl_pin =self.bitcell.get_pin(self.bitcell_bl)
        self.bitcell_br_pin =self.bitcell.get_pin(self.bitcell_br)

        if self.bitcell_bl_pin.layer == "m1":
            self.bitline_layer = "m1"
            self.en_layer = "m2"
        else:
            self.bitline_layer = "m2"
            self.en_layer = "m1"
            
        # Creates the netlist and layout
        # Since it has variable height, it is not a pgate.
        self.create_netlist()
        if not OPTS.netlist_only:
            self.create_layout()
            self.DRC_LVS()

    def get_bl_names(self):
        return "bl"

    def get_br_names(self):
        return "br"

    def create_netlist(self):
        self.add_pins()
        self.add_ptx()
        self.create_ptx()
        
    def create_layout(self):

        self.place_ptx()
        self.connect_poly()
        self.route_en()
        self.place_nwell_and_contact()
        self.route_vdd_rail()
        self.route_bitlines()
        self.connect_to_bitlines()

    def add_pins(self):
        self.add_pin_list(["bl", "br", "en_bar", "vdd"],
                          ["OUTPUT", "OUTPUT", "INPUT", "POWER"])

    def add_ptx(self):
        """
        Initializes the upper and lower pmos
        """
        self.pmos = factory.create(module_type="ptx",
                                   width=self.ptx_width,
                                   tx_type="pmos")
        self.add_mod(self.pmos)

    def route_vdd_rail(self):
        """
        Adds a vdd rail at the top of the cell
        """
        
        # Adds the rail across the width of the cell
        vdd_position = vector(0.5 * self.width, self.height)
        layer_width = drc("minwidth_" + self.en_layer)
        self.add_rect_center(layer=self.en_layer,
                             offset=vdd_position,
                             width=self.width,
                             height=layer_width)

        pmos_pin = self.upper_pmos2_inst.get_pin("S")
        
        # center of vdd rail
        pmos_vdd_pos = vector(pmos_pin.cx(), vdd_position.y)
        self.add_path("m1", [pmos_pin.uc(), pmos_vdd_pos])
        
        # if enable is not on M1, the supply can be
        if self.en_layer != "m1":
            self.add_via_center(layers=self.m1_stack,
                                offset=pmos_vdd_pos)

        self.add_power_pin("vdd",
                           self.well_contact_pos,
                           vertical=True)
        
        # Hack for li layers
        if OPTS.tech_name == "s8":
            self.add_via_center(layers=self.li_stack,
                                offset=self.well_contact_pos)
        
    def create_ptx(self):
        """
        Create both the upper_pmos and lower_pmos to the module
        """

        self.lower_pmos_inst = self.add_inst(name="lower_pmos",
                                             mod=self.pmos)
        self.connect_inst(["bl", "en_bar", "br", "vdd"])

        self.upper_pmos1_inst = self.add_inst(name="upper_pmos1",
                                              mod=self.pmos)
        self.connect_inst(["bl", "en_bar", "vdd", "vdd"])

        self.upper_pmos2_inst = self.add_inst(name="upper_pmos2",
                                              mod=self.pmos)
        self.connect_inst(["br", "en_bar", "vdd", "vdd"])
        
    def place_ptx(self):
        """
        Place both the upper_pmos and lower_pmos to the module
        """

        # reserve some offset to jog the bitlines
        self.initial_yoffset = self.pmos.active_offset.y + self.m2_pitch
        # Compute the other pmos2 location,
        # but determining offset to overlap the source and drain pins
        overlap_offset = self.pmos.get_pin("D").ll() - self.pmos.get_pin("S").ll()
        # This is how much the contact is placed inside the ptx active
        contact_xdiff = self.pmos.get_pin("S").lx()
        
        # adds the lower pmos to layout
        bl_xoffset = self.bitcell_bl_pin.lx()
        self.lower_pmos_position = vector(max(bl_xoffset - contact_xdiff,
                                              self.nwell_enclose_active),
                                          self.initial_yoffset)
        self.lower_pmos_inst.place(self.lower_pmos_position)

        # adds the upper pmos(s) to layout with 2 M2 tracks
        ydiff = self.pmos.height + self.m2_pitch
        self.upper_pmos1_pos = self.lower_pmos_position + vector(0, ydiff)
        self.upper_pmos1_inst.place(self.upper_pmos1_pos)

        # Second pmos to the right of the first
        upper_pmos2_pos = self.upper_pmos1_pos + overlap_offset
        self.upper_pmos2_inst.place(upper_pmos2_pos)
        
    def connect_poly(self):
        """
        Connects the upper and lower pmos together
        """

        offset = self.lower_pmos_inst.get_pin("G").ll()
        # connects the top and bottom pmos' gates together
        ylength = self.upper_pmos1_inst.get_pin("G").ll().y - offset.y
        self.add_rect(layer="poly",
                      offset=offset,
                      width=self.poly_width,
                      height=ylength)

        # connects the two poly for the two upper pmos(s)
        offset = offset + vector(0, ylength - self.poly_width)
        xlength = self.upper_pmos2_inst.get_pin("G").lx() \
                  - self.upper_pmos1_inst.get_pin("G").lx() \
                  + self.poly_width
        self.add_rect(layer="poly",
                      offset=offset,
                      width=xlength,
                      height=self.poly_width)

    def route_en(self):
        """
        Adds the en input rail, en contact/vias, and connects to the pmos
        """

        # adds the en contact to connect the gates to the en rail
        # midway in the 4 M2 tracks
        offset = self.lower_pmos_inst.get_pin("G").ul() \
                 + vector(0, 0.5 * self.m2_pitch)
        self.add_via_center(layers=self.poly_stack,
                            offset=offset)
        if self.en_layer == "m2":
            self.add_via_center(layers=self.m1_stack,
                                offset=offset)
        
        # adds the en rail on metal1
        self.add_layout_pin_segment_center(text="en_bar",
                                           layer=self.en_layer,
                                           start=offset.scale(0, 1),
                                           end=offset.scale(0, 1) + vector(self.width, 0))
                     
    def place_nwell_and_contact(self):
        """
        Adds a nwell tap to connect to the vdd rail
        """
        
        # adds the contact from active to metal1
        offset_height = self.upper_pmos1_inst.uy() + \
                        0.5 * contact.active_contact.height + \
                        self.nwell_extend_active
        self.well_contact_pos = self.upper_pmos1_inst.get_pin("D").center().scale(1, 0) + \
                                vector(0, offset_height)
        self.add_via_center(layers=self.active_stack,
                            offset=self.well_contact_pos,
                            implant_type="n",
                            well_type="n")

        self.height = self.well_contact_pos.y + contact.active_contact.height + self.m1_space

        # nwell should span the whole design since it is pmos only
        self.add_rect(layer="nwell",
                      offset=vector(0, 0),
                      width=self.width,
                      height=self.height)

    def route_bitlines(self):
        """
        Adds both bit-line and bit-line-bar to the module
        """
        layer_width = drc("minwidth_" + self.bitline_layer)
        layer_space = drc("{0}_to_{0}".format(self.bitline_layer))

        # adds the BL
        self.bl_xoffset = layer_space + 0.5 * layer_width
        top_pos = vector(self.bl_xoffset, self.height)
        pin_pos = vector(self.bl_xoffset, 0)
        self.add_path(self.bitline_layer, [top_pos, pin_pos])
        self.bl_pin = self.add_layout_pin_segment_center(text="bl",
                                                         layer=self.bitline_layer,
                                                         start=pin_pos,
                                                         end=top_pos)
        
        # adds the BR
        self.br_xoffset = self.width - layer_space - 0.5 * layer_width
        top_pos = vector(self.br_xoffset, self.height)
        pin_pos = vector(self.br_xoffset, 0)
        self.add_path(self.bitline_layer, [top_pos, pin_pos])
        self.br_pin = self.add_layout_pin_segment_center(text="br",
                                                         layer=self.bitline_layer,
                                                         start=pin_pos,
                                                         end=top_pos)

    def connect_to_bitlines(self):
        """
        Connect the bitlines to the devices
        """
        self.add_bitline_contacts()
        self.connect_pmos(self.lower_pmos_inst.get_pin("S"),
                          self.bl_xoffset)
        self.connect_pmos(self.lower_pmos_inst.get_pin("D"),
                          self.br_xoffset)
        
        self.connect_pmos(self.upper_pmos1_inst.get_pin("S"),
                          self.bl_xoffset)
        self.connect_pmos(self.upper_pmos2_inst.get_pin("D"),
                          self.br_xoffset)

    def add_bitline_contacts(self):
        """
        Adds contacts/via from metal1 to metal2 for bit-lines
        """

        # No contacts needed if M1
        if self.bitline_layer == "m1":
            return
        
        # BL
        lower_pin = self.lower_pmos_inst.get_pin("S")
        self.lower_via = self.add_via_center(layers=self.m1_stack,
                                             offset=lower_pin.center(),
                                             directions=("V", "V"))

        lower_pin = self.lower_pmos_inst.get_pin("D")
        self.lower_via = self.add_via_center(layers=self.m1_stack,
                                             offset=lower_pin.center(),
                                             directions=("V", "V"))
        
        # BR
        upper_pin = self.upper_pmos1_inst.get_pin("S")
        self.upper_via2 = self.add_via_center(layers=self.m1_stack,
                                              offset=upper_pin.center(),
                                              directions=("V", "V"))

        upper_pin = self.upper_pmos2_inst.get_pin("D")
        self.upper_via2 = self.add_via_center(layers=self.m1_stack,
                                              offset=upper_pin.center(),
                                              directions=("V", "V"))

    def connect_pmos(self, pmos_pin, bit_xoffset):
        """
        Connect a pmos pin to bitline pin
        """

        left_pos = vector(min(pmos_pin.cx(), bit_xoffset), pmos_pin.cy())
        right_pos = vector(max(pmos_pin.cx(), bit_xoffset), pmos_pin.cy())

        self.add_path(self.bitline_layer,
                      [left_pos, right_pos],
                      width=pmos_pin.height())
        
    def get_en_cin(self):
        """Get the relative capacitance of the enable in the precharge cell"""
        # The enable connect to three pmos gates
        # They all use the same size pmos.
        pmos_cin = self.pmos.get_cin()
        return 3 * pmos_cin
        
