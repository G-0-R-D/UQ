
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <float.h>

#define snap_fuzzy_is_null(NUM) ((NUM >= -SNAP_DOUBLE_MIN && NUM <= SNAP_DOUBLE_MIN) ? 1:0)

#define SNAP_DOUBLE_MIN DBL_MIN //0.000000000001
#define SNAP_DOUBLE_MAX DBL_MAX

#define SNAP_MIN(A, B) ((A < B) ? A : B)
#define SNAP_MAX(A, B) ((A > B) ? A : B)
#define SNAP_ABS(NUM) ((NUM < 0) ? NUM * -1 : NUM)

// XXX TODO this is duplicated from the SnapMatrix support lib
double SNAP_IDENTITY_MATRIX[16] = {
	1.0, 0.0, 0.0, 0.0,
	0.0, 1.0, 0.0, 0.0,
	0.0, 0.0, 1.0, 0.0,
	0.0, 0.0, 0.0, 1.0
};

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




#define _snap_extents_are_null(EXTENTS) (\
	(EXTENTS != NULL && ( \
	/*instead of fuzzy_is_null, since value must be positive (min <= max must be true)*/\
	EXTENTS[3]-EXTENTS[0] > SNAP_DOUBLE_MIN || \
	EXTENTS[4]-EXTENTS[1] > SNAP_DOUBLE_MIN || \
	EXTENTS[5]-EXTENTS[2] > SNAP_DOUBLE_MIN )  \
	) ? 0 : 1)/*note truth switch, since this is a negative statement*/

int snap_extents_are_null(double* EXTENTS){
	return _snap_extents_are_null(EXTENTS);
}

void snap_matrix_map_extents(double *matrix, double *extents, int is_delta, double *ANSWER){
	// NOTE: use inverted matrix to map back out

	snap_matrix_transform_point(matrix, extents, (double)!is_delta, ANSWER);
	snap_matrix_transform_point(matrix, extents + 3, (double)!is_delta, ANSWER + 3);

	// rotations may re-assign extents min/max order, make sure min <= max
	double tmp;
	int idx = -1;
	while (++idx < 3){

		if (ANSWER[idx] <= ANSWER[idx+3])
			continue;

		tmp = ANSWER[idx];
		ANSWER[idx] = ANSWER[idx+3];
		ANSWER[idx+3] = tmp;
	}
}

#define _snap_extents_contain_point(EXTENTS, POINT) (\
	(EXTENTS != NULL && POINT != NULL && (\
	/* extents are always aligned to axes, they have no concept of rotation
	also it is assumed max point is >= min point ALWAYS, it is an error otherwise
	but will just evaluate to outside of rect if min >= max*/\
	POINT[0] >= EXTENTS[0] && POINT[0] <= EXTENTS[3] && \
	POINT[1] >= EXTENTS[1] && POINT[1] <= EXTENTS[4] && \
	POINT[2] >= EXTENTS[2] && POINT[2] <= EXTENTS[5]) \
	) ? 1 : 0)

int snap_extents_contain_point(double* EXTENTS, double* POINT){
	return _snap_extents_contain_point(EXTENTS, POINT);
}



int snap_extents_diffmatrix(double* BASE_ext, double* ITEM_ext, int lock_scale, int uniform, double align_x, double align_y, double align_z, double* MATRIX_ANSWER){//, SnapNode* MSG){

	// calculates the matrix that would transform ITEM_ext to fit into BASE_ext
	// NOTE: the extents should have been mapped from their container matrices, and are being compared as peers

	if (!MATRIX_ANSWER){
		//snap_error("%s no matrix to write answer into!", SNAP_FUNCTION_NAME);
		return 1;//(any)"ERROR";
	}
	if (!(BASE_ext && ITEM_ext)){
		memcpy(MATRIX_ANSWER, SNAP_IDENTITY_MATRIX, 16 * sizeof (double));
		return 0;
	}

	//int uniform = 1;
	// centered (this will only have an effect if the object axis does not fill the allocation)
	//double align[] = {.5, .5, .5}; // TODO handle oversize properly too?
	double align[] = {align_x, align_y, align_z};
	// TODO align is a weighting, if 1 it means align the right side with the right side, if 0 it means align the left with the left, if .5 it means centered (regardless of scale, if bigger or smaller the side alignment is the same result...)

	/*
	{for_attr_in_SnapNode(MSG)
		if (attr == (any)"uniform"){
			uniform = snap_bool_as_int(value);
		}
		else if (attr == (any)"align"){
			snap_memcpy(align, value, 3 * sizeof (double));
		}
		else if (attr == (any)"x_align"){
			align[0] = *((double*)value);
		}
		else if (attr == (any)"y_align"){
			align[1] = *((double*)value);
		}
		else if (attr == (any)"z_align"){
			align[2] = *((double*)value);
		}
	}}
	*/

	double base_dims[3] = {
		BASE_ext[3] - BASE_ext[0],
		BASE_ext[4] - BASE_ext[1],
		BASE_ext[5] - BASE_ext[2],
		};


	//double item_origin[3] = {ITEM_ext[0], ITEM_ext[1], ITEM_ext[3]};
	//double *item_origin = ITEM_ext;
	double item_dims[3] = {
		SNAP_MAX(ITEM_ext[3] - ITEM_ext[0], SNAP_DOUBLE_MIN),
		SNAP_MAX(ITEM_ext[4] - ITEM_ext[1], SNAP_DOUBLE_MIN),
		SNAP_MAX(ITEM_ext[5] - ITEM_ext[2], SNAP_DOUBLE_MIN),
		};

	//snap_out("ITEM_dims w(%.2lf) h(%.2lf) d(%.2lf)", item_dims[0], item_dims[1], item_dims[2]);

	// TODO negative scaling?
	double scale[3] = {1,1,1};
	if (!lock_scale){
		// we only want to consider valid entries and there might not be any!  so flag if they are valid
		unsigned int valid_indexes = 0;
		int i = -1;
		while (++i < 3){
			//if (item_dims[i] != 0){ // TODO fuzzy is null?
			//if (item_dims[i] > 0.001){//
			if (!snap_fuzzy_is_null(item_dims[i])){
				scale[i] = SNAP_MAX(base_dims[i] / item_dims[i], SNAP_DOUBLE_MIN);
				//snap_out("scale[%d] %lf base(%lf) item(%lf)", i, scale[i], base_dims[i], item_dims[i]);
				//printf("scale[%d] %lf base(%lf) item(%lf)\n", i, scale[i], base_dims[i], item_dims[i]);
				valid_indexes |= (1 << i);
			}
		}
		if (uniform){
			// if uniform we scale uniformly by the smallest scale
			if (valid_indexes){

				// a uniform scale can only be as large as the smallest axis
				// (the one that scales the least) TODO if it gets smaller then isn't it the biggest?
				double smallest;

				switch (valid_indexes){
					// number represents binary flags in reverse
					case 1: // 001 -> 100
						smallest = scale[0];
						break;
					case 2: // 010 -> 010
						smallest = scale[1];
						break;
					case 3: // 011 -> 110
						smallest = SNAP_MIN(scale[0], scale[1]);
						break;
					case 4: // 100 -> 001
						smallest = scale[2];
						break;
					case 5: // 101 -> 101
						smallest = SNAP_MIN(scale[0], scale[2]);
						break;
					case 6: // 110 -> 011
						smallest = SNAP_MIN(scale[1], scale[2]);
						break;
					case 7: // 111 -> 111
						smallest = SNAP_MIN(scale[0], SNAP_MIN(scale[1], scale[2]));
						break;
					default:
						//snap_error("INVALID INDEXES?? %d", valid_indexes);
						return 1;//(any)"ERROR";
				}

				printf("smallest %lf\n", smallest);
				scale[0] = smallest;
				scale[1] = smallest;
				scale[2] = smallest;

			}

			// else scale is all 1's, which it should already be
		}
	}

	/*
	double tm[16] = {
		scale[0],0,0, BASE_ext[0] + ((base_dims[0] - (item_dims[0] * scale[0])) * align[0]) - (ITEM_ext[0] * scale[0]),
		0,scale[1],0, BASE_ext[1] + ((base_dims[1] - (item_dims[1] * scale[1])) * align[1]) - (ITEM_ext[1] * scale[1]),
		0,0,scale[2], BASE_ext[2] + ((base_dims[2] - (item_dims[2] * scale[2])) * align[2]) - (ITEM_ext[2] * scale[2]),
		0,0,0, 1
		};
	*/
	// 'unused'
	MATRIX_ANSWER[1] = 0.;
	MATRIX_ANSWER[2] = 0.;
	MATRIX_ANSWER[4] = 0.;
	MATRIX_ANSWER[6] = 0.;
	MATRIX_ANSWER[8] = 0.;
	MATRIX_ANSWER[9] = 0.;
	MATRIX_ANSWER[12] = 0.;
	MATRIX_ANSWER[13] = 0.;
	MATRIX_ANSWER[14] = 0.;
	MATRIX_ANSWER[15] = 1.;	

	// translation
	MATRIX_ANSWER[3] = BASE_ext[0] + ((base_dims[0] - (item_dims[0] * scale[0])) * align[0]) - (ITEM_ext[0] * scale[0]);
	MATRIX_ANSWER[7] = BASE_ext[1] + ((base_dims[1] - (item_dims[1] * scale[1])) * align[1]) - (ITEM_ext[1] * scale[1]);
	MATRIX_ANSWER[11] = BASE_ext[2] + ((base_dims[2] - (item_dims[2] * scale[2])) * align[2]) - (ITEM_ext[2] * scale[2]);

	// scale
	MATRIX_ANSWER[0] = scale[0];
	MATRIX_ANSWER[5] = scale[1];
	MATRIX_ANSWER[10] = scale[2];

	//printf("matrix(\n");
	//printf("\t%lf, %lf, %lf, %lf\n", MATRIX_ANSWER[0], MATRIX_ANSWER[1], MATRIX_ANSWER[2], MATRIX_ANSWER[3]);
	//printf("\t%lf, %lf, %lf, %lf\n", MATRIX_ANSWER[4], MATRIX_ANSWER[5], MATRIX_ANSWER[6], MATRIX_ANSWER[7]);
	//printf("\t%lf, %lf, %lf, %lf\n", MATRIX_ANSWER[8], MATRIX_ANSWER[9], MATRIX_ANSWER[10], MATRIX_ANSWER[11]);
	//printf("\t%lf, %lf, %lf, %lf\n", MATRIX_ANSWER[12], MATRIX_ANSWER[13], MATRIX_ANSWER[14], MATRIX_ANSWER[15]);
	//printf(")\n");

	return 0;
}

/* TODO put this in python, it requires class awareness...
int snap_extents_fit(double* BASE_ext, SnapNode ITEM, SnapNode* MSG){
	// fits ITEM inside of BASE_ext by translating and scaling ITEM's matrix by the difference

	double ITEM_ext[] = {0.,0.,0., 0.,0.,0.};
	snap_event(&ITEM, "GET", "extents", ITEM_ext);
	
	// XXX TODO use snap_event(self, "GET", "extents", ext);
	//double* BASE_extents_src = (double*)snap_getattr_at(self, "_extents_", IDX_SnapMetrics__extents_);
	//double* ITEM_extents_src = (double*)snap_getattr_at(&ITEM, "_extents_", IDX_SnapMetrics__extents_);

	if (snap_extents_are_null(BASE_ext) || snap_extents_are_null(ITEM_ext)){
		snap_warning("invalid extents for fit operation");
		snap_extents_print(BASE_ext);
		snap_extents_print(ITEM_ext);
		return (any)"ERROR";
	}

	// localized for assign below
	double* ITEM_matrix = (double*)snap_getattr_at(&ITEM, "_matrix_", IDX_SnapMatrix__matrix_);
	if (!ITEM_matrix){
		snap_error("no matrix on item!");
		return (any)"ERROR";
	}

	// extents are local to item, we want them in item parent space (the two are compared as peers)
	snap_map_extents(ITEM_matrix, ITEM_ext, 0, ITEM_ext);

	double tm[16];
	if (_snap_extents_diffmatrix(BASE_ext, ITEM_ext, tm, MSG) == (any)"ERROR"){
		snap_error("%s unable to calculate diffmatrix", SNAP_FUNCTION_NAME);
		return (any)"ERROR";
	}

	snap_matrix_transform(ITEM_matrix, tm, NULL, ITEM_matrix);

	return NULL;
}
*/

void snap_extents_mix(double* A, double* B, double* ANSWER){
	// combines two extents together into one
	ANSWER[0] = SNAP_MIN(A[0], B[0]);
	ANSWER[1] = SNAP_MIN(A[1], B[1]);
	ANSWER[2] = SNAP_MIN(A[2], B[2]);
	ANSWER[3] = SNAP_MAX(A[3], B[3]);
	ANSWER[4] = SNAP_MAX(A[4], B[4]);
	ANSWER[5] = SNAP_MAX(A[5], B[5]);
}

void snap_extents_ensure_correct(double* EXTENTS){
	// makes sure min < max or swaps them
	double tmp;
	if (EXTENTS[3] < EXTENTS[0]){
		tmp = EXTENTS[3];
		EXTENTS[3] = EXTENTS[0];
		EXTENTS[0] = tmp;
	}
	if (EXTENTS[4] < EXTENTS[1]){
		tmp = EXTENTS[4];
		EXTENTS[4] = EXTENTS[1];
		EXTENTS[1] = tmp;
	}
	if (EXTENTS[5] < EXTENTS[2]){
		tmp = EXTENTS[5];
		EXTENTS[5] = EXTENTS[2];
		EXTENTS[2] = tmp;
	}
}
