<?xml version="1.0" encoding="UTF-8"?>
<!-- $Id: DC.xsl,v 1.2 2007/03/28 05:28:39 jerome Exp $

     This file is part of CDS Invenio.
     Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007 CERN.

     CDS Invenio is free software; you can redistribute it and/or
     modify it under the terms of the GNU General Public License as
     published by the Free Software Foundation; either version 2 of the
     License, or (at your option) any later version.

     CDS Invenio is distributed in the hope that it will be useful, but
     WITHOUT ANY WARRANTY; without even the implied warranty of
     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
     General Public License for more details.  

     You should have received a copy of the GNU General Public License
     along with CDS Invenio; if not, write to the Free Software Foundation, Inc.,
     59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
-->
<!--
<name>DC</name>
<description>XML Dublin Core</description>
-->

<!-- 

This stylesheet transforms a MARCXML input into an DC output.     
This stylesheet is provided only as an example of transformation.

-->

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:marc="http://www.loc.gov/MARC21/slim" xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:fn="http://cdsweb.cern.ch/bibformat/fn" exclude-result-prefixes="marc fn">
  <xsl:output method="xml"  indent="yes" encoding="UTF-8" omit-xml-declaration="yes" />
  <xsl:template match="/">
    <xsl:if test="collection">
      <oai_dc:collection xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd">
        <xsl:for-each select="collection">
          <xsl:for-each select="record">
            <oai_dc:dc><xsl:apply-templates select="."/></oai_dc:dc>
          </xsl:for-each>
        </xsl:for-each>
      </oai_dc:collection>
    </xsl:if>
    <xsl:if test="record">
      <oai_dc:dc xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd" xmlns:dc="http://purl.org/dc/elements/1.1/"><xsl:apply-templates/></oai_dc:dc>
    </xsl:if>
  </xsl:template>

  <xsl:template match="record">
    <xsl:for-each select="controlfield[@tag=001]">
      <dc:identifier><xsl:text>http://infoscience.epfl.ch/record/</xsl:text><xsl:value-of select="."/></dc:identifier>
    </xsl:for-each>
    
    <xsl:for-each select="datafield[@tag=024 and @ind1=7]">	
      <xsl:if test="starts-with(subfield[@code='a'],'10.5075')">
        <dc:identifier><xsl:value-of select="subfield[@code='2']"/><xsl:text>:</xsl:text><xsl:value-of select="subfield[@code='a']"/></dc:identifier>
      </xsl:if>
    </xsl:for-each>
    
    <xsl:choose>
      <xsl:when test="datafield[@tag=041]">
        <xsl:for-each select="datafield[@tag=041]">
          <dc:language><xsl:value-of select="subfield[@code='a']"/></dc:language>
        </xsl:for-each>
      </xsl:when>
      <xsl:otherwise>
        <dc:language><xsl:text>en</xsl:text></dc:language>
      </xsl:otherwise>
    </xsl:choose>
    
    <xsl:for-each select="datafield[@tag=245]">
      <dc:title>
        <xsl:value-of select="subfield[@code='a']"/>
        <xsl:if test="subfield[@code='b']">
          <xsl:text>: </xsl:text><xsl:value-of select="subfield[@code='b']"/>
        </xsl:if>
      </dc:title>
    </xsl:for-each>

    <xsl:for-each select="datafield[@tag=260]">
      <dc:date><xsl:value-of select="subfield[@code='c'] "/></dc:date>
	  
    </xsl:for-each>
	
	<xsl:for-each select="datafield[@tag=260]/subfield[@code = 'b']">
		<dc:publisher>
			<xsl:value-of select="."/>
				<xsl:for-each select="../subfield[@code = 'a']">
					<xsl:text> (</xsl:text>
					<xsl:value-of select="."/>
					<xsl:text>)</xsl:text>
				</xsl:for-each>
		</dc:publisher>
    </xsl:for-each>
    
    <xsl:for-each select="datafield[@tag=520]">
      <dc:description><xsl:value-of select="subfield[@code='a']"/></dc:description>
    </xsl:for-each>
    
    <xsl:for-each select="datafield[@tag=653 and @ind1=1]">
      <dc:subject><xsl:value-of select="subfield[@code='a']"/></dc:subject>
    </xsl:for-each>
    
    <xsl:for-each select="datafield[@tag=700]">
      <xsl:choose>
        <xsl:when test="subfield[@code='e'] = 'dir.'">
          <dc:contributor><xsl:value-of select="subfield[@code='a']"/></dc:contributor>
        </xsl:when>
        <xsl:otherwise>
          <dc:creator><xsl:value-of select="subfield[@code='a']"/></dc:creator>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
    
    <dc:type><xsl:text>Text</xsl:text></dc:type>
    <dc:format><xsl:text>text/html</xsl:text></dc:format>
  </xsl:template>
</xsl:stylesheet>