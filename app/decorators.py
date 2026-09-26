from django.shortcuts import redirect


def unauthenticated_required (view_func):
	def wrapper (request,*args,**kwarg):
		if request.user.is_authenticated:
			return redirect('home')
		else:
			return view_func(request,*args,**kwarg)
	return wrapper