import sys, subprocess
import numpy as np


# ========================================================= #
# ===  vtk_makeUnstructuredGrid class                   === #
# ========================================================= #
class vtk_makeUnstructuredGrid():
    # ------------------------------------------------- #
    # --- class Initiator                           --- #
    # ------------------------------------------------- #
    def __init__( self, vtkFile=None, Data=None, Node=None, Elem=None, \
                  xAxis=None, yAxis=None, zAxis=None, VectorData=False, DataFormat="ascii" ):
        # --- [1-1] Arguments                       --- #
        if ( vtkFile is None ): vtkFile = "out.vtu"
        # --- [1-2] Variables Settings              --- #
        self.vtkFile     = vtkFile
        self.vtkContents = ''
        self.vtkEndTags  = ''
        self.Data        = Data
        self.Node        = Node
        self.Elem        = Elem
        self.DataFormat  = DataFormat
        self.VectorData  = VectorData
        self.DataDims    = None
        self.LILJLK      = None
        # --- [1-3] Routines                        --- #
        self.vtk_add_VTKFileTag  ( datatype="UnstructuredGrid" )
        self.vtk_add_UnstructuredGridTag( Data=self.Data, Node=self.Node, Elem=self.Elem, VectorData=self.VectorData )
        self.vtk_writeFile()
        
    # ------------------------------------------------- #
    # --- vtk_add_VTKFileTag                        --- #
    # ------------------------------------------------- #
    def vtk_add_VTKFileTag( self, datatype=None ):
        # ------------------------------------------------- #
        # --- [1] Add XML Definition & VTKFile Tag      --- #
        # ------------------------------------------------- #
        if ( datatype is None ): datatype = "UnstructuredGrid"
        self.vtkContents  += '<?xml version="1.0"?>\n'
        self.vtkContents  += '<VTKFile type="{0}">\n'.format( datatype )
        self.vtkEndTags    = '</VTKFile>'     + '\n' + self.vtkEndTags
        
    # ------------------------------------------------- #
    # --- vtk_add_UnstructuredGridTag               --- #
    # ------------------------------------------------- #
    def vtk_add_UnstructuredGridTag( self, Data=None , Node    =None, Elem=None, DataName=None, \
                                     VectorData=False, DataDims=None, WholeExtent=None, \
                                     PointData =False, CellData=True ):
        # ------------------------------------------------- #
        # --- [1] Arguments                             --- #
        # ------------------------------------------------- #
        if ( DataName is None ): DataName = "Data"
        self.prepareData( Data=Data, VectorData=VectorData )
        if ( Data     is None ): return()
        if ( Elem     is None ): return()
        if ( Node     is None ): return()
        if   ( VectorData is True  ):
            Scl_or_Vec   = "Vectors"
        elif ( VectorData is False ):
            Scl_or_Vec   = "Scalars"
        nNodes = Node.shape[0]
        nElems = Elem.shape[0]
        # ------------------------------------------------- #
        # --- [2] UnstructuredGrid & Piece Tag  Begin   --- #
        # ------------------------------------------------- #
        self.vtkContents  += '<UnstructuredGrid>\n'
        self.vtkContents  += '<Piece  NumberOfPoints="{0}" NumberOfCells="{1}">\n'.format( nNodes, nElems )
        # ------------------------------------------------- #
        # --- [3] PointData / CellData / Coordinates    --- #
        # ------------------------------------------------- #
        if   ( PointData is True ):
            self.vtkContents  += '<PointData {0}="{1}">\n'.format( Scl_or_Vec, DataName )
            self.vtkContents  += self.vtk_add_DataArray( Data=Data, DataName=DataName )
            self.vtkContents  += '</PointData>\n'
        elif ( CellData  is True ):
            self.vtkContents  += '<CellData {0}="{1}">\n' .format( Scl_or_Vec, DataName  )
            self.vtkContents  += self.vtk_add_DataArray( Data=Data, DataName=DataName )
            self.vtkContents  += '</CellData>\n'
        self.vtkContents  += '<Points>\n'
        self.vtkContents  += self.vtk_add_DataArray( Data=Node, DataName="Nodes", VectorData=True )
        self.vtkContents  += '</Points>\n'
        self.vtkContents  += self.vtk_add_Cells( Elem=Elem )
        # ------------------------------------------------- #
        # --- [4] Close UnstructuredGrid & Piece Tag    --- #
        # ------------------------------------------------- #
        self.vtkContents  += '</Piece>\n'         
        self.vtkContents  += '</UnstructuredGrid>\n'


    # ========================================================= #
    # ===  vtk_add_Cells                                    === #
    # ========================================================= #
    def vtk_add_Cells( self, Elem=None, ElementType=None ):
        if ( Elem is None ): sys.exit( "[vtk_add_Cell] Elem == ???" )
        ret    = ""
        nElems = Elem.shape[0]
        nVerts = Elem.shape[1]
        if ( ElementType is None ):
            if ( nVerts == 1 ): ElementType = "vertex"
            if ( nVerts == 2 ): ElementType = "line"
            if ( nVerts == 3 ): ElementType = "triangle"
            if ( nVerts == 4 ): ElementType = "tetra"
            if ( nVerts == 5 ): ElementType = "pyramid"
            if ( nVerts == 6 ): ElementType = "hexahedron"
        ElementTypeTable = { "vertex":1, "poly_vertex":2, "line":3, "poly_line":4, "triangle":5, \
                             "polygon":7, "pixel":8, "quad":9, "tetra":10, "voxel":11, "hexahedron":12, \
                             "hexa":12, "pyramid":14 }
        types   = np.ones( (nElems,), dtype=np.int64 ) * ElementTypeTable[ElementType]
        offsets = ( np.arange( nElems, dtype=np.int64 ) + 1 ) * nVerts
        connect = np.array( Elem, dtype=np.int64 )
        ret   += "<Cells>\n"
        ret   += self.vtk_add_DataArray( Data=connect , DataName="connectivity", VectorData=True, nComponents=1 )
        ret   += self.vtk_add_DataArray( Data=offsets , DataName="offsets"      )
        ret   += self.vtk_add_DataArray( Data=types   , DataName="types"        )
        ret   += "</Cells>\n"
        return( ret )

    
    # ------------------------------------------------- #
    # --- vtk_add_DataArray                         --- #
    # ------------------------------------------------- #
    def vtk_add_DataArray( self, Data=None, DataName=None, DataFormat=None, DataType=None, nComponents=None, nData=None, VectorData=False ):
        if ( Data        is None ): sys.exit( "[vtk_add_DataArray -@makeUnstructuredGrid-] Data     == ??? " )
        if ( DataName    is None ): sys.exit( "[vtk_add_DataArray -@makeUnstructuredGrid-] DataName == ??? " )
        if ( DataFormat  is None ): DataFormat  = self.DataFormat
        if ( DataType    is None ): DataType    = self.inquiryData( Data=Data, ret_DataType   =True, VectorData=VectorData )
        if ( nComponents is None ): nComponents = self.inquiryData( Data=Data, ret_nComponents=True, VectorData=VectorData )
        if ( nData       is None ): nData       = self.inquiryData( Data=Data, ret_nData      =True, VectorData=VectorData )
        ret  = ""
        ret += '<DataArray Name="{0}" type="{1}" NumberOfComponents="{2}" format="{3}">\n'\
                                 .format( DataName, DataType, nComponents, DataFormat )
        lines = ""
        if ( VectorData ):
            for line in Data:
                lines += ( " ".join( [ str( val ) for val in line ] ) + "\n" )
        else:
            for line in np.ravel( Data ):
                lines += "{0} ".format( line )
            lines += "\n"
        ret += lines
        ret += '</DataArray>\n'
        return( ret )
    
    
    # ------------------------------------------------- #
    # --- vtk_writeFile                             --- #
    # ------------------------------------------------- #
    def vtk_writeFile( self, vtkFile=None ):
        if ( vtkFile is None ): vtkFile = self.vtkFile
        with open( vtkFile, "w" ) as f:
            f.write( self.vtkContents )
            f.write( self.vtkEndTags  )
        subprocess.call( ( "xmllint --format --encode utf-8 {0} -o {0}"\
                           .format( vtkFile ) ).split() )
        print( "[vtk_writeFile-@makeUnstructuredGrid-] VTK File output :: {0}".format( vtkFile ) )


    # ------------------------------------------------- #
    # --- inquiryData                               --- #
    # ------------------------------------------------- #
    def inquiryData( self, Data=None, VectorData=False, ret_DataType=False, ret_nComponents=False, ret_nData=False ):
        if ( Data is None ): sys.exit( "[inquiryData-@vtk_makeUnstructuredGrid-] Data  == ??? " )
        # ------------------------------------------------- #
        # --- [1] DataType Check                        --- #
        # ------------------------------------------------- #
        if ( type(Data) is not np.ndarray ):
            sys.exit( "[inquiryData-@vtk_makeUnstructuredGrid-] Data should be np.ndarray [ERROR]" )
        if ( Data.dtype == np.int32   ): DataType = "Int32"
        if ( Data.dtype == np.int64   ): DataType = "Int64"
        if ( Data.dtype == np.float32 ): DataType = "Float32"
        if ( Data.dtype == np.float64 ): DataType = "Float64"
        # ------------------------------------------------- #
        # --- [2] Data Shape Check                      --- #
        # ------------------------------------------------- #
        if ( VectorData is True ):
            nComponents = Data.shape[-1]
            nData       = np.size( Data[-1][:] )
        else:
            nComponents = 1
            nData       = np.size( Data[:]    )
        # ------------------------------------------------- #
        # --- [3] Return                                --- #
        # ------------------------------------------------- #
        if ( ret_DataType    ): return( DataType    )
        if ( ret_nComponents ): return( nComponents )
        if ( ret_nData       ): return( nData       )
        return( { "DataType":DataType, "nComponents":nComponents, "nData":nData } )

        
    # ------------------------------------------------- #
    # --- prepareData                               --- #
    # ------------------------------------------------- #
    def prepareData( self, Data=None, VectorData=False ):
        # ------------------------------------------------- #
        # --- [1] Data Array Type/Shape Check           --- #
        # ------------------------------------------------- #
        if ( Data is None   ): return()
        if ( type(Data) is not np.ndarray ):
            sys.exit( "[prepareData-@vtk_makeUnstructuredGrid-] Data should be np.ndarray [ERROR]" )
        if ( Data.ndim >= 5 ):
            sys.exit( "[prepareData-@vtk_makeUnstructuredGrid-] incorrect Data size ( ndim >= 5 ) [ERROR]" )
        # ------------------------------------------------- #
        # --- [2] DataDims & LILJLK Check               --- #
        # ------------------------------------------------- #
        if ( VectorData is True ):
            self.DataDims   = Data.shape[-1]
            self.LILJLK     = Data.shape[:-1]
        else:
            self.DataDims   = 1
            self.LILJLK     = Data.shape[:]
        # ------------------------------------------------- #
        # --- [3] for 2D Data                           --- #
        # ------------------------------------------------- #
        if ( len( self.LILJLK ) == 2 ):
            self.LILJLK = self.LILJLK + (1,)
            Data        = Data.reshape( self.LILJLK )
        if ( len( self.LILJLK ) == 1 ):
            self.LILJLK = self.LILJLK + (1,1,)
            Data        = Data.reshape( self.LILJLK )


            
# ======================================== #
# ===  実行部                          === #
# ======================================== #
if ( __name__=="__main__" ):
    elemFile = "elems.dat"
    nodeFile = "nodes.dat"
    with open( elemFile, "r" ) as f:
        rElem = np.loadtxt( f )
        Elem  = np.array( rElem[:,1:], dtype=np.int64 )
    with open( nodeFile, "r" ) as f:
        Node  = np.loadtxt( f )
    Data    = np.zeros( (Elem.shape[0]) )
    for iE,el in enumerate( Elem ):
        Data[iE] = 0.25 * ( Node[el[0],2] + Node[el[1],2] + Node[el[2],2] + Node[el[3],2] )
    vtk     = vtk_makeUnstructuredGrid( Data=Data, Elem=Elem, Node=Node )
        
