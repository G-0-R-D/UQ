
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <float.h>

#define snap_fuzzy_is_null(NUM) ((NUM >= -SNAP_DOUBLE_MIN && NUM <= SNAP_DOUBLE_MIN) ? 1:0)

#define SNAP_DOUBLE_MIN DBL_MIN //0.000000000001
#define SNAP_DOUBLE_MAX DBL_MAX

// TODO what if matrix is initialized through engine api?  so then re-mapping coordinates can be done for the engine?  So Y down could be used in OpenGL... etc?
//	TODO is it possible to put the coordinate shift onto the context?  so each context can define it's own shift?  should be...
//		-- could this be done as an initial multiplication at the beginning of the render?  offset the context render orientation?  how to keep individual items rendering the same direction, like images?


// for fast copies to reset matrices to identity
double SNAP_IDENTITY_MATRIX[16] = {
	1.0, 0.0, 0.0, 0.0,
	0.0, 1.0, 0.0, 0.0,
	0.0, 0.0, 1.0, 0.0,
	0.0, 0.0, 0.0, 1.0
};

void snap_matrix_multiply(double* A, double* B, double* ANSWER){

	/*
	column major:
	| xx xy xz x0 | rightx upx forwardx posx
	| yx yy yz y0 | righty upy forwardy posy
	| zx zy zz z0 | rightz upz forwardz posz
	| wx wy wz w0 | rightw upw forwardw posw
	pre-multiplied ie. A * B

	as flat array indexes:
	0  1  2  3
	4  5  6  7
	8  9  10 11
	12 13 14 15

	00 01 02 03
	10 11 12 13
	20 21 22 23
	30 31 32 33
	*/

	//https://stackoverflow.com/questions/30236805/how-to-optimize-4x4-matrix-multiplication
	
	// unpack A
	double a00 = A[0];
	double a01 = A[1];
	double a02 = A[2];
	double a03 = A[3];

	double a10 = A[4];
	double a11 = A[5];
	double a12 = A[6];
	double a13 = A[7];

	double a20 = A[8];
	double a21 = A[9];
	double a22 = A[10];
	double a23 = A[11];

	double a30 = A[12];
	double a31 = A[13];
	double a32 = A[14];
	double a33 = A[15];

	// unpack B
	double b00 = B[0];
	double b01 = B[1];
	double b02 = B[2];
	double b03 = B[3];

	double b10 = B[4];
	double b11 = B[5];
	double b12 = B[6];
	double b13 = B[7];

	double b20 = B[8];
	double b21 = B[9];
	double b22 = B[10];
	double b23 = B[11];

	double b30 = B[12];
	double b31 = B[13];
	double b32 = B[14];
	double b33 = B[15];

	// calculate
	/*
	ANSWER[0] = a00*b00 + a10*b01 + a20*b02 + a30*b03;
	ANSWER[1] = a01*b00 + a11*b01 + a21*b02 + a31*b03;
	ANSWER[2] = a02*b00 + a12*b01 + a22*b02 + a32*b03;
	ANSWER[3] = a03*b00 + a13*b01 + a23*b02 + a33*b03;

	ANSWER[4] = a00*b10 + a10*b11 + a20*b12 + a30*b13;
	ANSWER[5] = a01*b10 + a11*b11 + a21*b12 + a31*b13;
	ANSWER[6] = a02*b10 + a12*b11 + a22*b12 + a32*b13;
	ANSWER[7] = a03*b10 + a13*b11 + a23*b12 + a33*b13;

	ANSWER[8] = a00*b20 + a10*b21 + a20*b22 + a30*b23;
	ANSWER[9] = a01*b20 + a11*b21 + a21*b22 + a31*b23;
	ANSWER[10] = a02*b20 + a12*b21 + a22*b22 + a32*b23;
	ANSWER[11] = a03*b20 + a13*b21 + a23*b22 + a33*b23;

	ANSWER[12] = a00*b30 + a10*b31 + a20*b32 + a30*b33;
	ANSWER[13] = a01*b30 + a11*b31 + a21*b32 + a31*b33;
	ANSWER[14] = a02*b30 + a12*b31 + a22*b32 + a32*b33;
	ANSWER[15] = a03*b30 + a13*b31 + a23*b32 + a33*b33;
	*/

	// row of A against columns of B (premultiplied; row-major; A * B)
	ANSWER[0] = a00*b00 + a01*b10 + a02*b20 + a03*b30;
	ANSWER[1] = a00*b01 + a01*b11 + a02*b21 + a03*b31;
	ANSWER[2] = a00*b02 + a01*b12 + a02*b22 + a03*b32;
	ANSWER[3] = a00*b03 + a01*b13 + a02*b23 + a03*b33;

	ANSWER[4] = a10*b00 + a11*b10 + a12*b20 + a13*b30;
	ANSWER[5] = a10*b01 + a11*b11 + a12*b21 + a13*b31;
	ANSWER[6] = a10*b02 + a11*b12 + a12*b22 + a13*b32;
	ANSWER[7] = a10*b03 + a11*b13 + a12*b23 + a13*b33;

	ANSWER[8] = a20*b00 + a21*b10 + a22*b20 + a23*b30;
	ANSWER[9] = a20*b01 + a21*b11 + a22*b21 + a23*b31;
	ANSWER[10] = a20*b02 + a21*b12 + a22*b22 + a23*b32;
	ANSWER[11] = a20*b03 + a21*b13 + a22*b23 + a23*b33;

	ANSWER[12] = a30*b00 + a31*b10 + a32*b20 + a33*b30;
	ANSWER[13] = a30*b01 + a31*b11 + a32*b21 + a33*b31;
	ANSWER[14] = a30*b02 + a31*b12 + a32*b22 + a33*b32;
	ANSWER[15] = a30*b03 + a31*b13 + a32*b23 + a33*b33;
}

// TODO rename this to snap_matrix_transform_point to be clearer in usage intention
void snap_matrix_transform_point(double* matrix, double* point, double delta, double* ANSWER){

	// delta is int 0 or 1 but making it double so it mixes into calculations
	// NOTE: this means set delta to 1.0 to include translation and to 0.0 to exclude translation

	// https://www.scratchapixel.com/lessons/mathematics-physics-for-computer-graphics/geometry/transforming-points-and-vectors

	/*
	point represents the translation component of another matrix that we want to map into or multiply by this matrix

	1 0 0 x
	0 1 0 y
	0 0 1 z
	0 0 0 1

	00 01 02 03
	10 11 12 13
	20 21 22 23
	30 31 32 33
	*/

	delta = delta < 1; // invert so logic is include delta = 1, exclude delta = 0

	double m00 = matrix[0];
	double m01 = matrix[1];
	double m02 = matrix[2];
	double m03 = matrix[3];

	double m10 = matrix[4];
	double m11 = matrix[5];
	double m12 = matrix[6];
	double m13 = matrix[7];

	double m20 = matrix[8];
	double m21 = matrix[9];
	double m22 = matrix[10];
	double m23 = matrix[11];

	//double m30 = matrix[12];
	//double m31 = matrix[13];
	//double m32 = matrix[14];
	//double m33 = matrix[15];

	// unpack vector
	double v0 = point[0];
	double v1 = point[1];
	double v2 = point[2];
	//double v3 = 1;//vec3[3];

	// position is column vector (translation), need to multiply by rows of matrix!
	ANSWER[0] = m00*v0 + m01*v1 + m02*v2 + m03*delta;//*v3;
	ANSWER[1] = m10*v0 + m11*v1 + m12*v2 + m13*delta;//*v3;
	ANSWER[2] = m20*v0 + m21*v1 + m22*v2 + m23*delta;//*v3;
	//ANSWER[3] = m30*v0 + m31*v1 + m32*v2 + m33*delta;//*v3;

	// was ANSWER[idx]: 3, 7, 11, 15
	//ANSWER[0] = m03*b00 + m13*b01 + m23*b02 + m33*b03;
	//ANSWER[1] = m03*b10 + m13*b11 + m23*b12 + m33*b13;
	//ANSWER[2] = m03*b20 + m13*b21 + m23*b22 + m33*b23;
	//ANSWER[3] = m03*b30 + m13*b31 + m23*b32 + m33*b33;

	//ANSWER[0] = m03*1 + m13*0 + m23*0 + m33*v0;
	//ANSWER[1] = m03*0 + m13*1 + m23*0 + m33*v1;
	//ANSWER[2] = m03*0 + m13*0 + m23*1 + m33*v2;
	//ANSWER[3] = m03*0 + m13*0 + m23*0 + m33*v3;

	//ANSWER[0] = m03 + m33*v0;
	//ANSWER[1] = m13 + m33*v1;
	//ANSWER[2] = m23 + m33*v2;
	//ANSWER[3] = m33*v3;
}
// TODO rename these to lowercase if they operate on double* matrix


// https://stackoverflow.com/questions/1148309/inverting-a-4x4-matrix
// gluInvertMatrix in MESA GLU library
int snap_matrix_invert_glu_style(double* m, double* ANSWER){

    double det;
    int i;

	double m0 = m[0];
	double m1 = m[1];
	double m2 = m[2];
	double m3 = m[3];
	double m4 = m[4];
	double m5 = m[5];
	double m6 = m[6];
	double m7 = m[7];
	double m8 = m[8];
	double m9 = m[9];
	double m10 = m[10];
	double m11 = m[11];
	double m12 = m[12];
	double m13 = m[13];
	double m14 = m[14];
	double m15 = m[15];

    ANSWER[0] = m5  * m10 * m15 - 
             m5  * m11 * m14 - 
             m9  * m6  * m15 + 
             m9  * m7  * m14 +
             m13 * m6  * m11 - 
             m13 * m7  * m10;

    ANSWER[4] = -m4  * m10 * m15 + 
              m4  * m11 * m14 + 
              m8  * m6  * m15 - 
              m8  * m7  * m14 - 
              m12 * m6  * m11 + 
              m12 * m7  * m10;

    ANSWER[8] = m4  * m9 * m15 - 
             m4  * m11 * m13 - 
             m8  * m5 * m15 + 
             m8  * m7 * m13 + 
             m12 * m5 * m11 - 
             m12 * m7 * m9;

    ANSWER[12] = -m4  * m9 * m14 + 
               m4  * m10 * m13 +
               m8  * m5 * m14 - 
               m8  * m6 * m13 - 
               m12 * m5 * m10 + 
               m12 * m6 * m9;

    ANSWER[1] = -m1  * m10 * m15 + 
              m1  * m11 * m14 + 
              m9  * m2 * m15 - 
              m9  * m3 * m14 - 
              m13 * m2 * m11 + 
              m13 * m3 * m10;

    ANSWER[5] = m0  * m10 * m15 - 
             m0  * m11 * m14 - 
             m8  * m2 * m15 + 
             m8  * m3 * m14 + 
             m12 * m2 * m11 - 
             m12 * m3 * m10;

    ANSWER[9] = -m0  * m9 * m15 + 
              m0  * m11 * m13 + 
              m8  * m1 * m15 - 
              m8  * m3 * m13 - 
              m12 * m1 * m11 + 
              m12 * m3 * m9;

    ANSWER[13] = m0  * m9 * m14 - 
              m0  * m10 * m13 - 
              m8  * m1 * m14 + 
              m8  * m2 * m13 + 
              m12 * m1 * m10 - 
              m12 * m2 * m9;

    ANSWER[2] = m1  * m6 * m15 - 
             m1  * m7 * m14 - 
             m5  * m2 * m15 + 
             m5  * m3 * m14 + 
             m13 * m2 * m7 - 
             m13 * m3 * m6;

    ANSWER[6] = -m0  * m6 * m15 + 
              m0  * m7 * m14 + 
              m4  * m2 * m15 - 
              m4  * m3 * m14 - 
              m12 * m2 * m7 + 
              m12 * m3 * m6;

    ANSWER[10] = m0  * m5 * m15 - 
              m0  * m7 * m13 - 
              m4  * m1 * m15 + 
              m4  * m3 * m13 + 
              m12 * m1 * m7 - 
              m12 * m3 * m5;

    ANSWER[14] = -m0  * m5 * m14 + 
               m0  * m6 * m13 + 
               m4  * m1 * m14 - 
               m4  * m2 * m13 - 
               m12 * m1 * m6 + 
               m12 * m2 * m5;

    ANSWER[3] = -m1 * m6 * m11 + 
              m1 * m7 * m10 + 
              m5 * m2 * m11 - 
              m5 * m3 * m10 - 
              m9 * m2 * m7 + 
              m9 * m3 * m6;

    ANSWER[7] = m0 * m6 * m11 - 
             m0 * m7 * m10 - 
             m4 * m2 * m11 + 
             m4 * m3 * m10 + 
             m8 * m2 * m7 - 
             m8 * m3 * m6;

    ANSWER[11] = -m0 * m5 * m11 + 
               m0 * m7 * m9 + 
               m4 * m1 * m11 - 
               m4 * m3 * m9 - 
               m8 * m1 * m7 + 
               m8 * m3 * m5;

    ANSWER[15] = m0 * m5 * m10 - 
              m0 * m6 * m9 - 
              m4 * m1 * m10 + 
              m4 * m2 * m9 + 
              m8 * m1 * m6 - 
              m8 * m2 * m5;

    det = m0 * ANSWER[0] + m1 * ANSWER[4] + m2 * ANSWER[8] + m3 * ANSWER[12];

    if (det == 0) return -1;

    det = 1.0 / det;

    for (i = 0; i < 16; i++)
        ANSWER[i] = ANSWER[i] * det;

    return 0;
}

// https://stackoverflow.com/questions/1148309/inverting-a-4x4-matrix (answer 2 by willnode)
int snap_matrix_invert(double* m, double* ANSWER){

	double det;

	double m00 = m[0];
	double m01 = m[1];
	double m02 = m[2];
	double m03 = m[3];
	double m10 = m[4];
	double m11 = m[5];
	double m12 = m[6];
	double m13 = m[7];
	double m20 = m[8];
	double m21 = m[9];
	double m22 = m[10];
	double m23 = m[11];
	double m30 = m[12];
	double m31 = m[13];
	double m32 = m[14];
	double m33 = m[15];	

	double A2323 = m22 * m33 - m23 * m32 ;
	double A1323 = m21 * m33 - m23 * m31 ;
	double A1223 = m21 * m32 - m22 * m31 ;
	double A0323 = m20 * m33 - m23 * m30 ;
	double A0223 = m20 * m32 - m22 * m30 ;
	double A0123 = m20 * m31 - m21 * m30 ;
	double A2313 = m12 * m33 - m13 * m32 ;
	double A1313 = m11 * m33 - m13 * m31 ;
	double A1213 = m11 * m32 - m12 * m31 ;
	double A2312 = m12 * m23 - m13 * m22 ;
	double A1312 = m11 * m23 - m13 * m21 ;
	double A1212 = m11 * m22 - m12 * m21 ;
	double A0313 = m10 * m33 - m13 * m30 ;
	double A0213 = m10 * m32 - m12 * m30 ;
	double A0312 = m10 * m23 - m13 * m20 ;
	double A0212 = m10 * m22 - m12 * m20 ;
	double A0113 = m10 * m31 - m11 * m30 ;
	double A0112 = m10 * m21 - m11 * m20 ;

	det = m00 * ( m11 * A2323 - m12 * A1323 + m13 * A1223 ) 
		- m01 * ( m10 * A2323 - m12 * A0323 + m13 * A0223 ) 
		+ m02 * ( m10 * A1323 - m11 * A0323 + m13 * A0123 ) 
		- m03 * ( m10 * A1223 - m11 * A0223 + m12 * A0123 ) ;

	if (det == 0)
		return 1; //return (any)"ERROR";

	det = 1 / det;

	ANSWER[0] = det *   ( m11 * A2323 - m12 * A1323 + m13 * A1223 );
	ANSWER[1] = det * - ( m01 * A2323 - m02 * A1323 + m03 * A1223 );
	ANSWER[2] = det *   ( m01 * A2313 - m02 * A1313 + m03 * A1213 );
	ANSWER[3] = det * - ( m01 * A2312 - m02 * A1312 + m03 * A1212 );
	ANSWER[4] = det * - ( m10 * A2323 - m12 * A0323 + m13 * A0223 );
	ANSWER[5] = det *   ( m00 * A2323 - m02 * A0323 + m03 * A0223 );
	ANSWER[6] = det * - ( m00 * A2313 - m02 * A0313 + m03 * A0213 );
	ANSWER[7] = det *   ( m00 * A2312 - m02 * A0312 + m03 * A0212 );
	ANSWER[8] = det *   ( m10 * A1323 - m11 * A0323 + m13 * A0123 );
	ANSWER[9] = det * - ( m00 * A1323 - m01 * A0323 + m03 * A0123 );
	ANSWER[10] = det *   ( m00 * A1313 - m01 * A0313 + m03 * A0113 );
	ANSWER[11] = det * - ( m00 * A1312 - m01 * A0312 + m03 * A0112 );
	ANSWER[12] = det * - ( m10 * A1223 - m11 * A0223 + m12 * A0123 );
	ANSWER[13] = det *   ( m00 * A1223 - m01 * A0223 + m02 * A0123 );
	ANSWER[14] = det * - ( m00 * A1213 - m01 * A0213 + m02 * A0113 );
	ANSWER[15] = det *   ( m00 * A1212 - m01 * A0212 + m02 * A0112 );

	return 0;
}
//#define SnapMatrix_invert snap_matrix_invert

void snap_matrix_transpose(double* self, double* ANSWER){
	/*
	rows swap with columns across diagonal
	| A1 | A2 | A3 | A4 |T    | A1 | B1 | C1 | D1 |
	| B1 | B2 | B3 | B4 |     | A2 | B2 | C2 | D2 |
	| C1 | C2 | C3 | C4 |  =  | A3 | B3 | C3 | D3 |
	| D1 | D2 | D3 | D4 |     | A4 | B4 | C4 | D4 |

	0  1  2  3
	4  5  6  7
	8  9  10 11
	12 13 14 15

	0  4  8  12
	1  5  9  13
	2  6  10 14
	3  7  11 15

	*/

	// intermediary matrix, otherwise matrix_transpose(A, A) will not work correctly!
	double intermediary[16] = {
		self[0],
		self[4],
		self[8],
		self[12],
		self[1],
		self[5],
		self[9],
		self[13],
		self[2],
		self[6],
		self[10],
		self[14],
		self[3],
		self[7],
		self[11],
		self[15],
		};

	memcpy(ANSWER, intermediary, 16 * sizeof (double));

}
//#define SnapMatrix_transpose snap_matrix_transpose


void snap_matrix_print(double *matrix){
	fprintf(stdout, "matrix:\n");
	int x;
	int y;
	int idx = 0;
	for (y=0; y < 4; y++){
		for (x=0; x < 4; x++){
			fprintf(stdout, "%lf ", matrix[idx]);
			idx++;
			}
		fprintf(stdout, "\n");
		}
	fprintf(stdout, "\n");
	fflush(stdout);
}
//#define SnapMatrix_print snap_matrix_print





int snap_matrix_transform(double* self, double* TRANSFORM, double* PARENT, double* ANSWER){
	// NOTE this is kind of swapped because we want to transform self,
	// which means multiplying self by the transform, not multiplying the transform by self!
	// ie. this is an operation on self
	// matrix_multiply is A * B, but this is an operation ON self, so it is TRANSFORM * self (or B * A)
	if (PARENT){		
		// PARENT * TRANSFORM * PARENT.inverse() * self

		/*
		TODO multiply in reverse order so only one buffer matrix needed (same result?)
		*/
		//double a[16];
		#if 0
		double inverse[16];
		if (snap_matrix_invert(PARENT, (double*)inverse) == (any)"ERROR"){
			snap_error("matrix_transform uninvertable parent matrix"); // can we continue ignoring parent?
			return (any)"ERROR";
		}
		snap_matrix_multiply(PARENT, TRANSFORM, a);
		snap_matrix_multiply(a, (double*)inverse, a);
		snap_matrix_multiply(a, self, ANSWER);
		#else
		// using ANSWER as intermediary buffer XXX doesn't work if input is same as output! (self == ANSWER)
		double a[16];
		if (snap_matrix_invert(PARENT, a)){
			//snap_error("matrix_transform: uninvertable parent matrix!");
			//memcpy(ANSWER, SNAP_IDENTITY_MATRIX, 16 * sizeof (double)); // set to identity for niceties
			return 1; //(any)"ERROR";
		}
		snap_matrix_multiply(a, self, a);
		snap_matrix_multiply(TRANSFORM, a, a);
		snap_matrix_multiply(PARENT, a, ANSWER);
		#endif
	}
	else {
		// TRANSFORM * self
		snap_matrix_multiply(TRANSFORM, self, ANSWER);
	}
	return 0;
}


int snap_matrix_scale(double* self, double x, double y, double z, double* PARENT, double* ANSWER){
	double mat[16] = {x,0,0,0, 0,y,0,0, 0,0,z,0, 0,0,0,1};
	return snap_matrix_transform(self, (double*)mat, PARENT, ANSWER);
}

int snap_matrix_rotate(double* self, double angle, double x, double y, double z, double* PARENT, double* ANSWER){
	// rotate about an axis defined by x,y,z
	// from .../qt5/src/gui/math3d/qmatrix4x4.cpp -> QMatrix4x4::rotate

	if (angle == 0.0){
		memcpy(ANSWER, self, 16 * sizeof (double));
		return 0;
	}

	// TODO just assign to
	double m[16] = {1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1};
	double s, c; // sin, cos values

	if (angle == 90.0 || angle == -270.0){
		s = 1.0;
		c = 0.0;
	}
	else if (angle == -90.0 || angle == 270.0){
		s = -1.0;
		c = 0.0;
	}
	else if (angle == 180.0 || angle == -180.0){
		s = 0.0;
		c = -1.0;
	}
	else {
		double a = angle * M_PI / 180.0;
		s = sin(a);
		c = cos(a);
	}
	int quick = 0;
	if (x == 0.0){
		if (y == 0.0){
			if (z != 0.0){
				// Rotate around the Z axis.
	            //m[0][0] = c;
				m[0] = c;
	            //m.m[1][1] = c;
				m[5] = c;
	            if (z < 0.0){
	                //m.m[1][0] = s;
					m[4] = s;
	                //m.m[0][1] = -s;
					m[1] = -s;
	            }
				else {
	                //m.m[1][0] = -s;
					m[4] = -s;
	                //m.m[0][1] = s;
					m[1] = s;
	            }
	            // m.flagBits = General; ???
	            quick = 1;				
			}
		}
		else if (z == 0.0) {
	        // Rotate around the Y axis.
	        //m.m[0][0] = c;
			m[0] = c;
	        //m.m[2][2] = c;
			m[10] = c;
	        if (y < 0.0) {
	            //m.m[2][0] = -s;
				m[8] = -s;
	            //m.m[0][2] = s;
				m[2] = s;
	        }
			else {
	            //m.m[2][0] = s;
				m[8] = s;
	            //m.m[0][2] = -s;
				m[2] = -s;
	        }
	        //m.flagBits = General;
	        quick = 1;
	    }
	}
	else if (y == 0.0 && z == 0.0) {
	    // Rotate around the X axis.
	    //m.setToIdentity();
	    //m.m[1][1] = c;
		m[5] = c;
	    //m.m[2][2] = c;
		m[10] = c;
	    if (x < 0.0) {
	        //m.m[2][1] = s;
			m[9] = s;
	        //m.m[1][2] = -s;
			m[6] = -s;
	    }
		else {
	        //m.m[2][1] = -s;
			m[9] = -s;
	        //m.m[1][2] = s;
			m[6] = s;
	    }
	    //m.flagBits = General;
	    quick = 1;
	}

	if (!quick) {
	    double len = x * x + y * y + z * z;
		// https://doc.qt.io/qt-5/qtglobal.html#qFuzzyCompare
	    //if (!qFuzzyIsNull(len - 1.0) && !qFuzzyIsNull(len)) {
		if (!snap_fuzzy_is_null(len - 1.0) && !snap_fuzzy_is_null(len)){
	        len = sqrt(len);
	        x /= len;
	        y /= len;
	        z /= len;
	    }
	    double ic = 1.0 - c;
	 	m[0] = x * x * ic + c;
	    m[4] = x * y * ic - z * s;
	    m[8] = x * z * ic + y * s;

	    m[1] = y * x * ic + z * s;
	    m[5] = y * y * ic + c;
	    m[9] = y * z * ic - x * s;

	    m[2] = x * z * ic - y * s;
	    m[6] = y * z * ic + x * s;
	    m[10] = z * z * ic + c;
		/*
	    m.m[0][0] = x * x * ic + c;
	    m.m[1][0] = x * y * ic - z * s;
	    m.m[2][0] = x * z * ic + y * s;
	    m.m[3][0] = 0.0f;
	    m.m[0][1] = y * x * ic + z * s;
	    m.m[1][1] = y * y * ic + c;
	    m.m[2][1] = y * z * ic - x * s;
	    m.m[3][1] = 0.0f;
	    m.m[0][2] = x * z * ic - y * s;
	    m.m[1][2] = y * z * ic + x * s;
	    m.m[2][2] = z * z * ic + c;
	    m.m[3][2] = 0.0f;
	    m.m[0][3] = 0.0f;
	    m.m[1][3] = 0.0f;
	    m.m[2][3] = 0.0f;
	    m.m[3][3] = 1.0f;
		*/
	}

	return snap_matrix_transform(self, (double*)m, PARENT, ANSWER);
	//memcpy(ANSWER, m, 16 * sizeof (double));
	/*
	int flags = flagBits;
	*this *= m;
	if (flags != Identity)
	    flagBits = flags | Rotation;
	else
	    flagBits = Rotation;
	*/
}

int snap_matrix_translate(double* self, double x, double y, double z, double* PARENT, double* ANSWER){
	double mat[16] = {1,0,0,x, 0,1,0,y, 0,0,1,z, 0,0,0,1};
	return snap_matrix_transform(self, (double*)mat, PARENT, ANSWER);
}

int snap_matrix_decompose(double* self, double* POS_XYZ, double* QUAT_XYZW, double* SCALE_4x4){
	// http://www.pbr-book.org/3ed-2018/Geometry_and_Transformations/Animating_Transformations.html#eq:animated-transformation
	//snap_warning("%s not implemented", SNAP_FUNCTION_NAME);
	fprintf(stdout, "warning: snap_matrix_decompose not implemented");
	return 1; // error
}



