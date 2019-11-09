import sys, subprocess
import numpy as np


# ========================================================= #
# ===  vtk_makeStructuredGrid class                     === #
# ========================================================= #
class vtk_makeStructuredGrid():
    # ------------------------------------------------- #
    # --- class Initiator                           --- #
    # ------------------------------------------------- #
    def __init__( self, vtkFile=None, Data=None, Axis=None, \
                  xAxis=None, yAxis=None, zAxis=None, VectorData=False, DataFormat="ascii" ):
        # --- [1-1] Arguments                       --- #
        if ( vtkFile is None ): vtkFile = "out.vts"
        # --- [1-2] Variables Settings              --- #
        self.vtkFile     = vtkFile
        self.vtkContents = ''
        self.vtkEndTags  = ''
        self.Data        = Data
        self.Axis        = Axis
        self.DataFormat  = DataFormat
        self.VectorData  = VectorData
        self.DataDims    = None
        self.LILJLK      = None
        # --- [1-3] Routines                        --- #
        self.vtk_add_VTKFileTag  ( datatype="StructuredGrid" )
        self.prepareAxis ( xAxis=xAxis, yAxis=yAxis, zAxis=zAxis )
        self.vtk_add_StructuredGridTag( Data=self.Data, Axis=self.Axis, VectorData=self.VectorData )
        self.vtk_writeFile()
        
    # ------------------------------------------------- #
    # --- vtk_add_VTKFileTag                        --- #
    # ------------------------------------------------- #
    def vtk_add_VTKFileTag( self, datatype=None ):
        # ------------------------------------------------- #
        # --- [1] Add XML Definition & VTKFile Tag      --- #
        # ------------------------------------------------- #
        if ( datatype is None ): datatype = "StructuredGrid"
        self.vtkContents  += '<?xml version="1.0"?>\n'
        self.vtkContents  += '<VTKFile type="{0}">\n'.format( datatype )
        self.vtkEndTags    = '</VTKFile>'     + '\n' + self.vtkEndTags
        
    # ------------------------------------------------- #
    # --- vtk_add_StructuredGridTag                 --- #
    # ------------------------------------------------- #
    def vtk_add_StructuredGridTag( self, Data=None, Axis=None, DataName=None, \
                                   VectorData=False, DataDims=None, WholeExtent=None, \
                                   PointData=True, CellData=False ):
        # ------------------------------------------------- #
        # --- [1] Arguments                             --- #
        # ------------------------------------------------- #
        if ( DataName is None ): DataName = "Data"
        self.prepareData( Data=Data, VectorData=VectorData )
        if   ( VectorData is True  ):
            Scl_or_Vec   = "Vectors"
        elif ( VectorData is False ):
            Scl_or_Vec   = "Scalars"
        if ( WholeExtent is None   ): WholeExtent  = " ".join( [ "0 {0}".format( max(s-1,0) ) for s in list( self.LILJLK ) ] )
        # ------------------------------------------------- #
        # --- [2] StructuredGrid & Piece Tag  Begin     --- #
        # ------------------------------------------------- #
        self.vtkContents  += '<StructuredGrid WholeExtent="{0}">\n'.format( WholeExtent )
        self.vtkContents  += '<Piece Extent="{0}">\n'              .format( WholeExtent )
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
        self.vtkContents  += self.vtk_add_DataArray( Data=Axis, DataName="Axis", VectorData=True )
        self.vtkContents  += '</Points>\n'
        # ------------------------------------------------- #
        # --- [4] Close StructuredGrid & Piece Tag      --- #
        # ------------------------------------------------- #
        self.vtkContents  += '</Piece>\n'         
        self.vtkContents  += '</StructuredGrid>\n'
        
    # ------------------------------------------------- #
    # --- vtk_add_DataArray                         --- #
    # ------------------------------------------------- #
    def vtk_add_DataArray( self, Data=None, DataName=None, DataFormat=None, DataType=None, nComponents=None, nData=None, VectorData=False ):
        if ( Data        is None ): sys.exit( "[vtk_add_DataArray -@makeStructuredGrid-] Data     == ??? " )
        if ( DataName    is None ): sys.exit( "[vtk_add_DataArray -@makeStructuredGrid-] DataName == ??? " )
        if ( DataFormat  is None ): DataFormat  = self.DataFormat
        if ( DataType    is None ): DataType    = self.inquiryData( Data=Data, ret_DataType   =True, VectorData=VectorData )
        if ( nComponents is None ): nComponents = self.inquiryData( Data=Data, ret_nComponents=True, VectorData=VectorData )
        if ( nData       is None ): nData       = self.inquiryData( Data=Data, ret_nData      =True, VectorData=VectorData )
        ret  = ""
        ret += '<DataArray Name="{0}" type="{1}" NumberOfComponents="{2}" format="{3}">\n'\
                                 .format( DataName, DataType, nComponents, DataFormat )
        lines = ""
        if ( nComponents == 1 ):
            for line in np.ravel( Data ):
                lines += "{0} ".format( line )
            lines += "\n"
        else:
            for line in Data:
                lines += ( " ".join( [ str( val ) for val in line ] ) + "\n" )
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
        print( "[vtk_writeFile-@makeStructuredGrid-] VTK File output :: {0}".format( vtkFile ) )


    # ------------------------------------------------- #
    # --- inquiryData                               --- #
    # ------------------------------------------------- #
    def inquiryData( self, Data=None, VectorData=False, ret_DataType=False, ret_nComponents=False, ret_nData=False ):
        if ( Data is None ): sys.exit( "[inquiryData-@vtk_makeStructuredGrid-] Data  == ??? " )
        # ------------------------------------------------- #
        # --- [1] DataType Check                        --- #
        # ------------------------------------------------- #
        if ( type(Data) is not np.ndarray ):
            sys.exit( "[inquiryData-@vtk_makeStructuredGrid-] Data should be np.ndarray [ERROR]" )
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
    # --- prepareAxis                               --- #
    # ------------------------------------------------- #
    def prepareAxis( self, xAxis=None, yAxis=None, zAxis=None, Data=None ):
        if ( ( self.Axis is None ) and ( self.Data is not None ) ):
            if ( zAxis is None ): zAxis = np.array( [0.0] )
            if ( yAxis is None ): yAxis = np.array( [0.0] )
            if ( xAxis is None ): xAxis = np.array( [0.0] )
            xg,yg,zg  = np.meshgrid( xAxis,yAxis,zAxis,indexing='xy' )
            self.Axis = np.concatenate( [ np.ravel(xg)[:,np.newaxis], \
                                          np.ravel(yg)[:,np.newaxis], \
                                          np.ravel(zg)[:,np.newaxis] ], axis=1 )

        
    # ------------------------------------------------- #
    # --- prepareData                               --- #
    # ------------------------------------------------- #
    def prepareData( self, Data=None, VectorData=False ):
        # ------------------------------------------------- #
        # --- [1] Data Array Type/Shape Check           --- #
        # ------------------------------------------------- #
        if ( Data is None   ): return()
        if ( type(Data) is not np.ndarray ):
            sys.exit( "[prepareData-@vtk_makeStructuredGrid-] Data should be np.ndarray [ERROR]" )
        if ( Data.ndim >= 5 ):
            sys.exit( "[prepareData-@vtk_makeStructuredGrid-] incorrect Data size ( ndim >= 5 ) [ERROR]" )
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
    x1Range = [-1.0,+1.0]
    x2Range = [-1.0,+1.0]
    size    = ( 5,5 )
    xAxis   = np.linspace( x1Range[0], x1Range[1], size[0] )
    yAxis   = np.linspace( x2Range[0], x2Range[1], size[1] )
    zAxis   =    np.zeros( (1,) )
    import genGrid.Gaussian2D as gs2
    gau     = gs2.Gaussian2D( x1Range=x1Range, x2Range=x2Range, size=size )
    vtk     = vtk_makeStructuredGrid( Data=gau, xAxis=xAxis, yAxis=yAxis, zAxis=zAxis )
