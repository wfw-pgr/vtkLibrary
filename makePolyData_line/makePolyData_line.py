import sys, subprocess
import numpy as np


# ========================================================= #
# ===  vtk_makePolyData_line class                      === #
# ========================================================= #
class vtk_makePolyData_line():
    # ------------------------------------------------- #
    # --- class Initiator                           --- #
    # ------------------------------------------------- #
    def __init__( self, vtkFile=None, Data=None, xyz=None, \
                  VectorData=False, DataFormat="ascii", ):
        # --- [1-1] Arguments                       --- #
        if ( vtkFile is None ): vtkFile = "out.vtp"
        # --- [1-2] Variables Settings              --- #
        self.vtkFile      = vtkFile
        self.vtkContents  = ''
        self.vtkEndTags   = ''
        self.xyz          = xyz
        self.Data         = Data
        self.DataFormat   = DataFormat
        self.VectorData   = VectorData
        self.DataDims     = None
        self.NoLines      = None
        self.NoPoints     = None
        self.NoCoords     = None
        # --- [1-3] Routines                        --- #
        self.inquireLineData( xyz=self.xyz, Data=self.Data, VectorData=self.VectorData )
        self.vtk_add_VTKFileTag( datatype="PolyData" )
        self.vtk_add_PolyDataTag_Line( Data=self.Data, xyz=self.xyz, VectorData=self.VectorData )
        self.vtk_writeFile()

        
    # ------------------------------------------------- #
    # --- vtk_add_VTKFileTag                        --- #
    # ------------------------------------------------- #
    def vtk_add_VTKFileTag( self, datatype=None ):
        # ------------------------------------------------- #
        # --- [1] Add XML Definition & VTKFile Tag      --- #
        # ------------------------------------------------- #
        if ( datatype is None ): datatype = "ImageData"
        self.vtkContents  += '<?xml version="1.0"?>\n'
        self.vtkContents  += '<VTKFile type="{0}">\n'.format( datatype )
        self.vtkEndTags    = '</VTKFile>'     + '\n' + self.vtkEndTags

        
    # ------------------------------------------------- #
    # --- vtk_add_PolyDataTag                       --- #
    # ------------------------------------------------- #
    def vtk_add_PolyDataTag_Line( self, xyz=None, Data=None, VectorData=None, DataName="Line", \
                                  NoPoints=None, NoSegments=None, NoVerts=0, NoStrips=0, NoPolys=0 ):
        # ------------------------------------------------- #
        # --- [1] Arguments                             --- #
        # ------------------------------------------------- #
        if ( xyz        is None ): xyz        = self.xyz
        if ( Data       is None ): Data       = self.Data
        if ( VectorData is None ): VectorData = self.VectorData
        if ( NoPoints   is None ): NoPoints   = self.NoPoints
        if ( NoSegments is None ): NoSegments = self.NoPoints-1
        self.inquireLineData( xyz=xyz, Data=Data, VectorData=VectorData )
        connect, offsets   = self.prepareLineInfo( NoPoints=NoPoints )
        # ------------------------------------------------- #
        # --- [2] Open PolyData Tag                     --- #
        # ------------------------------------------------- #
        self.vtkContents  += '<PolyData>\n'
        self.vtkContents  += '<Piece NumberOfPoints="{0}" NumberOfLines="{1}" ' \
                             'NumberOfVerts="{2}" NumberOfStrips="{3}" NumberOfPolys="{4}">\n'\
                             .format( NoPoints, NoSegments, NoVerts, NoStrips, NoPolys )
        # ------------------------------------------------- #
        # --- [3] add Point & Line Data                 --- #
        # ------------------------------------------------- #
        #  -- [3-1] Data   -- #
        self.vtkContents  += '<PointData {0}="{1}">\n'.format( "Scalars", DataName )
        self.vtkContents  += self.vtk_add_DataArray( Data=Data, DataName=DataName, VectorData=False )
        self.vtkContents  += '</PointData>\n'
        #  -- [3-2] xyz points -- #
        self.vtkContents  += '<Points>\n'
        self.vtkContents  += self.vtk_add_DataArray( Data=xyz, DataName="points", VectorData=True )
        self.vtkContents  += '</Points>\n'
        #  -- [3-3] connectivity -- #
        self.vtkContents  += '<Lines>\n'
        self.vtkContents  += self.vtk_add_DataArray( Data=connect, DataName="connectivity", VectorData=False )
        self.vtkContents  += self.vtk_add_DataArray( Data=offsets, DataName="offsets"     , VectorData=False )
        self.vtkContents  += '</Lines>\n'
        # ------------------------------------------------- #
        # --- [4] Close PolyData Tags                   --- #
        # ------------------------------------------------- #
        self.vtkContents  += '</Piece>\n'
        self.vtkContents  += '</PolyData>\n'


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
        print( "[vtk_writeFile-@makePolyData_line-] VTK File output :: {0}".format( vtkFile ) )


    # ------------------------------------------------- #
    # --- inquiryData                               --- #
    # ------------------------------------------------- #
    def inquiryData( self, Data=None, VectorData=False, ret_DataType=False, ret_nComponents=False, ret_nData=False ):
        if ( Data is None ): sys.exit( "[inquiryData-@vtk_makeImageData-] Data  == ??? " )
        # ------------------------------------------------- #
        # --- [1] DataType Check                        --- #
        # ------------------------------------------------- #
        if ( type(Data) is not np.ndarray ):
            sys.exit( "[inquiryData-@vtk_makeImageData-] Data should be np.ndarray [ERROR]" )
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
    # --- vtk_inquireLineData                       --- #
    # ------------------------------------------------- #
    def inquireLineData( self, xyz=None, Data=None, VectorData=False ):
        # ------------------------------------------------- #
        # --- [1] Arguments                             --- #
        # ------------------------------------------------- #
        if ( xyz  is None ): xyz  = self.xyz
        if ( xyz  is None ): return( None )
        if ( Data is None ): Data = self.Data
        if ( type( xyz ) is not np.ndarray ):
            print( "[inquireLineData-@makePolyData_Line-] xyz should be np.ndarray [ERROR]" )
        if ( xyz.ndim >= 5 ):
            sys.exit( "[inquireLineData-@makePolyData_Line-] incorrect xyz size ( ndim >= 5 ) [ERROR]" )
        # ------------------------------------------------- #
        # --- [2] DataDims & LILJLK Check               --- #
        # ------------------------------------------------- #
        if ( VectorData is True ):
            self.NoPoints   = xyz.shape[0]
            self.NoCoords   = xyz.shape[1]
            self.NoLines    = xyz.shape[2]
        else:
            self.NoPoints   = xyz.shape[0]
            self.NoCoords   = xyz.shape[1]
            self.NoLines    = 1
            xyz             =  xyz.reshape(  xyz.shape + (1,) )
        # ------------------------------------------------- #
        # --- [3] prepare Data                          --- #
        # ------------------------------------------------- #
        if ( Data is None ): Data = np.zeros( ( self.NoPoints, self.NoLines ) )
        return( xyz, Data )

    
    # ------------------------------------------------- #
    # --- prepareLineInfo                           --- #
    # ------------------------------------------------- #
    def prepareLineInfo( self, NoPoints=None ):
        if ( NoPoints is None ): NoPoints = self.NoPoints
        connect = np.ravel( np.array( [ [ ik, ik+1 ] for ik in range( NoPoints-1 ) ] ) )
        offsets = np.ravel( np.array( [ 2*(ik+1)     for ik in range( NoPoints-1 ) ] ) )
        return( connect, offsets )

        
# ======================================== #
# ===  実行部                          === #
# ======================================== #
if ( __name__=="__main__" ):
    import myUtils.genArgs as gar
    args    = gar.genArgs()
    tAxis   = np.linspace( 0.0, 100.0, 10001 )
    xAxis   = np.cos( 2.*np.pi*tAxis        )
    yAxis   = np.sin( 2.*np.pi*tAxis        )
    zAxis   = np.sin( 2.*np.pi*tAxis * 0.01 )
    import myConvert.pilearr  as pil
    xyz     = np.transpose( pil.pilearr( (xAxis,yAxis,zAxis), axis=1 ) )
    Data    = np.copy( tAxis )
    vtk     = vtk_makePolyData_line( xyz=xyz, Data=Data )

